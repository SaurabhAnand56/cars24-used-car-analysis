"""
Cars24 Used Car Listings Scraper
---------------------------------
Cars24's listing pages are rendered client-side with React, so a plain
`requests.get()` only returns an empty HTML shell — BeautifulSoup alone
can't see the car data. This script uses Selenium to load the page like
a real browser, then hands the rendered HTML to BeautifulSoup to parse.

Install dependencies:
    pip install selenium beautifulsoup4 pandas webdriver-manager

Usage:
    python cars24_scraper.py
"""

import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Individual car detail links look like:
#   /buy-used-maruti-suzuki-swift-2019-cars-new-delhi-11033402/
# i.e. they contain "-cars-" AND end with a numeric listing ID.
# Category/nav links (e.g. "/buy-used-car-hyderabad/") don't match this.
LISTING_HREF_RE = re.compile(r"-cars-[a-z-]+-\d+/?$")

# Cars24 uses styled-components, so most text tags share a base class
# (e.g. "sc-bcXHqh") plus a second, field-specific hash class. We match
# on that second class since it's what distinguishes one field from
# another. These hash classes DO change across Cars24 deploys — if this
# starts returning None for everything, re-inspect the page in DevTools
# and update the class names below.
TITLE_CLASS = "bAcffq"       # e.g. "2023 Maruti Swift"
STOCK_TAG_CLASS = "iOTQvQ"   # e.g. "Cars24 Owned Stock"
PRICE_CLASS = "hvRpEM"       # e.g. "₹6.26 lakh"
LOCATION_CLASS = "bKVBht"    # e.g. "Kompally, Hyderabad"
SPEC_ITEM_CLASS = "kNDBvu"   # km / fuel / transmission / reg-state items

# The spec row (km, fuel type, transmission, reg state) all share the
# SAME class, so we can't tell them apart by class alone. Classify each
# by matching its text against a known pattern instead of relying on
# fixed position — robust even if Cars24 reorders these on the card.
KM_RE = re.compile(r"^[\d,]+\s*km$", re.IGNORECASE)
FUEL_TYPES = {"petrol", "diesel", "cng", "electric", "lpg", "hybrid"}
TRANSMISSIONS = {"manual", "automatic"}
REG_STATE_RE = re.compile(r"^[A-Z]{2}-?\d+$")


def get_driver(headless: bool = True):
    """Create a Chrome webdriver instance."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def text_by_class(container, tag_name, class_fragment):
    el = container.find(
        tag_name, class_=lambda c, cf=class_fragment: c and cf in c.split()
    )
    return el.get_text(strip=True) if el else None


def classify_specs(container):
    specs = {"km_driven": None, "fuel_type": None, "transmission": None, "reg_state": None}
    leftover = []
    spec_tags = container.find_all(
        "p", class_=lambda c: c and SPEC_ITEM_CLASS in c.split()
    )
    for tag in spec_tags:
        val = tag.get_text(strip=True)
        if KM_RE.match(val):
            specs["km_driven"] = val
        elif val.lower() in FUEL_TYPES:
            specs["fuel_type"] = val
        elif val.lower() in TRANSMISSIONS:
            specs["transmission"] = val
        elif REG_STATE_RE.match(val):
            specs["reg_state"] = val
        else:
            leftover.append(val)
    specs["other_specs"] = leftover
    return specs


def extract_cards(html: str):
    """Parse one snapshot of the page and return a list of car records
    for whichever listing cards are currently in the DOM."""
    soup = BeautifulSoup(html, "html.parser")
    all_links = soup.find_all("a", href=True)
    cards = [a for a in all_links if LISTING_HREF_RE.search(a["href"])]

    records = []
    for card in cards:
        href = card.get("href", "")
        # Only prepend the domain if the href is relative — Cars24
        # sometimes already returns absolute URLs.
        full_url = href if href.startswith("http") else "https://www.cars24.com" + href

        record = {
            "listing_url": full_url,
            "title": text_by_class(card, "span", TITLE_CLASS),
            "stock_type": text_by_class(card, "span", STOCK_TAG_CLASS),
            "price": text_by_class(card, "p", PRICE_CLASS),
            "location": text_by_class(card, "p", LOCATION_CLASS),
        }
        record.update(classify_specs(card))
        records.append(record)

    return records


def scrape_cars24(
    url: str,
    headless: bool = True,
    max_listings: int = 100,
    max_scroll_steps: int = 500,
    scroll_pause: float = 1.0,
    stagnant_limit: int = 6,
    checkpoint_path: str = None,
    checkpoint_every: int = 50,
) -> pd.DataFrame:
    """
    Scrape used-car listing cards from a Cars24 search results URL.

    max_listings      — stop once we've collected at least this many
                         unique cars (Hyderabad alone can have 2000+, so
                         scraping "all" of them means a lot of scrolling
                         — set this to whatever you actually need).
    max_scroll_steps   — hard cap on scroll iterations, regardless of
                         max_listings, so a stuck page can't loop forever.
    stagnant_limit     — stop early if this many consecutive scroll steps
                         produce zero new unique cars (means we've likely
                         hit the end of the results, or the page has
                         stopped loading more).
    checkpoint_path    — if set, save progress to this CSV every
                         `checkpoint_every` new cars, so a long run
                         (e.g. 1000 listings) doesn't lose everything if
                         it crashes or the site blocks the browser partway.
    checkpoint_every    — how many NEW unique cars between checkpoint saves.
    """
    driver = get_driver(headless=headless)
    collected = {}  # keyed by listing_url so re-seeing a card doesn't duplicate it

    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='-cars-']"))
            )
            # The href appearing doesn't mean the card's text has hydrated
            # yet — React fills in price/title/specs a beat later. Wait
            # for an actual price element before parsing anything, or the
            # first batch of cards gets captured with every field None
            # (and virtualization means we never get a second chance at
            # those exact cards once they scroll out of view).
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"p.{PRICE_CLASS}"))
            )
            time.sleep(1.5)  # small buffer for the rest of the card to settle
        except Exception:
            print("Timed out waiting for listings — page structure may have changed.")

        def merge_record(old, new):
            """Fill in any still-missing fields on `old` from `new` rather
            than overwriting — a card can be captured more than once
            across scroll steps, and a later pass may have data an
            earlier (mid-hydration) pass didn't."""
            merged = dict(old)
            for k, v in new.items():
                if k == "listing_url":
                    continue
                if k == "other_specs":
                    if not merged.get(k) and v:
                        merged[k] = v
                    continue
                if merged.get(k) is None and v is not None:
                    merged[k] = v
            return merged

        stagnant_steps = 0
        last_checkpoint_count = 0
        for step in range(max_scroll_steps):
            new_records = extract_cards(driver.page_source)
            before_count = len(collected)
            for rec in new_records:
                url_ = rec["listing_url"]
                if url_ in collected:
                    collected[url_] = merge_record(collected[url_], rec)
                else:
                    collected[url_] = rec
            gained = len(collected) - before_count

            if step % 10 == 0:
                print(f"Step {step}: {len(collected)} unique listings collected so far")

            if checkpoint_path and len(collected) - last_checkpoint_count >= checkpoint_every:
                pd.DataFrame(list(collected.values())).to_csv(checkpoint_path, index=False)
                last_checkpoint_count = len(collected)
                print(f"Checkpoint saved: {len(collected)} listings -> {checkpoint_path}")

            if len(collected) >= max_listings:
                break

            stagnant_steps = 0 if gained > 0 else stagnant_steps + 1
            if stagnant_steps >= stagnant_limit:
                break

            # Scroll by a fraction of the viewport rather than straight to
            # the bottom — the list is virtualized, so small steps give
            # the page time to mount new cards (and let us capture ones
            # about to be unloaded) instead of skipping over them.
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.75);")
            time.sleep(scroll_pause)

    finally:
        driver.quit()

    return pd.DataFrame(list(collected.values()))


if __name__ == "__main__":
    SEARCH_URL = "https://www.cars24.com/buy-used-cars-hyderabad/?sort=bestmatch&serveWarrantyCount=true&storeCityId=3686"

    # Adjust max_listings to however many cars you actually need —
    # scraping all 2000+ will take a while since it's real scroll+parse,
    # not a paginated API call.
    df = scrape_cars24(
        SEARCH_URL,
        headless=True,
        max_listings=1000,
        max_scroll_steps=2000,   # raised so we don't cap out before hitting max_listings
        scroll_pause=1.2,        # slightly longer pause — more time for cards to hydrate at scale
        stagnant_limit=10,       # a bit more patience before giving up early
        checkpoint_path="cars24_listings_checkpoint.csv",
        checkpoint_every=50,     # save progress every 50 new cars
    )
    print(f"Scraped {len(df)} listings")
    print(df.head())

    df.to_csv("cars24_listings.csv", index=False)
    print("Saved to cars24_listings.csv")
