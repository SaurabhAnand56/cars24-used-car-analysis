<div align="center">

# 🚗 Cars24 Used Car Data — Scraper & EDA

Scrape used-car listings from Cars24, clean the data, and explore pricing, mileage, fuel type, and location trends through visual analysis.

<p>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12"/>
  <img src="https://img.shields.io/badge/Selenium-Automation-43B02A?style=for-the-badge&logo=selenium&logoColor=white" alt="Selenium"/>
  <img src="https://img.shields.io/badge/BeautifulSoup-HTML%20Parsing-4B8BBE?style=for-the-badge&logo=python&logoColor=white" alt="BeautifulSoup"/>
  <img src="https://img.shields.io/badge/Pandas-Data%20Wrangling-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter"/>
  <img src="https://img.shields.io/badge/Matplotlib%20%2F%20Seaborn-Visualization-11557C?style=for-the-badge&logo=plotly&logoColor=white" alt="Matplotlib & Seaborn"/>
</p>

<p>
  <a href="https://github.com/SaurabhAnand56">
    <img src="https://img.shields.io/badge/GitHub-SaurabhAnand56-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="https://linkedin.com/in/saurabhanand56">
    <img src="https://img.shields.io/badge/LinkedIn-saurabhanand56-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
</p>

</div>

---

## 📌 About

This project scrapes used-car listings from [Cars24](https://www.cars24.com) for Hyderabad and takes them through a full analysis pipeline — **Data Collection → Data Understanding → Data Cleaning → Exploratory Data Analysis → Data Visualization → Business Insights & Recommendations** — to surface pricing trends, popular brands, fuel type mix, transmission split, and depreciation patterns by model year.

Since Cars24's listing pages are rendered client-side (React) and use a virtualized, infinite-scroll list, the scraper drives a real headless Chrome browser with **Selenium**, scrolling gradually and parsing with **BeautifulSoup** at every step so listings aren't lost as older cards unload from the DOM.

## ✨ Features

- Headless Chrome scraping via Selenium (handles JS-rendered content)
- Gradual-scroll strategy that correctly handles Cars24's virtualized listing list
- Field-level extraction: title, price, location, km driven, fuel type, transmission, registration state
- Regex-based classification for spec fields that share CSS classes
- Checkpointed scraping — periodic CSV saves so long runs survive a crash or block
- Structured data-understanding pass (dtypes, missing values, cardinality, raw-format samples) before any cleaning happens
- Full data-cleaning pipeline: numeric price/km conversion, year/brand/model extraction, transmission backfill, location splitting
- Non-visual EDA: categorical value counts, grouped price summaries, IQR-based outlier detection, price-per-km value analysis
- 10+ visualizations covering distributions, comparisons, correlation, and geography
- A closing insights section that computes real figures from the data (top brand/fuel share, price-by-transmission gap, depreciation curve, price/km correlation) and turns them into concrete recommendations

## 📂 File Structure

```
cars24-used-car-analysis/
│
├── cars24_scraper.py             # Selenium + BeautifulSoup scraper for Cars24 listings
├── cars24_listings.csv           # Raw scraped output
├── cars24_eda.ipynb              # Full pipeline: understanding, cleaning, EDA, visualization, insights
├── cars24_listings_cleaned.csv   # Cleaned, analysis-ready dataset
├── requirements.txt              # Python dependencies
├── LICENSE                       # MIT License
└── README.md                     # Project documentation
```

## 🛠️ Tech Stack

| Layer              | Technology                          |
|---------------------|--------------------------------------|
| Language            | Python 3.12                         |
| Browser Automation  | Selenium + webdriver-manager        |
| HTML Parsing        | BeautifulSoup4                      |
| Data Handling       | Pandas                              |
| Visualization       | Matplotlib, Seaborn                 |
| Analysis Environment| Jupyter Notebook                    |

## 📦 Dependencies

All dependencies are listed in [`requirements.txt`](./requirements.txt):

```
selenium>=4.20.0
webdriver-manager>=4.0.0
beautifulsoup4>=4.12.0
pandas>=2.2.0
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
jupyter>=1.0.0
```

Install them with:

```bash
pip install -r requirements.txt
```

> Google Chrome must also be installed locally — `webdriver-manager` handles downloading the matching ChromeDriver automatically.

## 🚀 Usage

**1. Scrape listings**

```bash
python cars24_scraper.py
```

Edit the `SEARCH_URL`, `max_listings`, and other parameters at the bottom of `cars24_scraper.py` to target a different city, budget range, or listing count.

**2. Run the analysis notebook**

```bash
jupyter notebook cars24_eda.ipynb
```

Run all cells to reproduce the full pipeline end to end, or open it directly — every output, table, and chart is already saved in the notebook.

## 📊 What the Notebook Covers

| Stage | What it does |
|---|---|
| **Data Understanding** | Structure, dtypes, missing-value breakdown, raw value samples, categorical cardinality |
| **Data Cleaning** | Numeric price/km conversion, year/brand/model extraction, transmission backfill, location split, dedup check |
| **Exploratory Data Analysis** | Descriptive stats, categorical value counts, grouped price summaries, IQR outlier detection, price-per-km ranking |
| **Data Visualization** | Price distribution, listings by year, top brands, fuel type mix, transmission/stock split, price by fuel/transmission, average price trend by year, correlation heatmap, price vs. km scatter, top localities |
| **Business Insights & Recommendations** | Computed findings on brand/fuel/transmission concentration, price gap by transmission, depreciation between oldest and newest model years, price/km correlation strength, and geographic concentration — each backed by an actual number from the data, followed by concrete recommendations |

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

## 👤 Author

**Saurabh Anand**
Data Analyst | MCA Fresher

<p>
  <a href="https://github.com/SaurabhAnand56">
    <img src="https://img.shields.io/badge/GitHub-SaurabhAnand56-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"/>
  </a>
  <a href="https://linkedin.com/in/saurabhanand56">
    <img src="https://img.shields.io/badge/LinkedIn-saurabhanand56-0A66C2?style=flat-square&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
</p>
