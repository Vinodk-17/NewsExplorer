# 🗞️ News Explorer

**Web Scraping and Analysis of News Using RSS Feeds**

## 🌍 Overview

**News Explorer** is a powerful Python-based application that extracts, analyzes, and visualizes news articles from over **25 countries** using RSS feeds and historical article scraping. It offers:
* Scrapes news from 24+ countries using RSS feeds
* Language detection
* Sentiment analysis
* Structured data storage (SQLite, CSV, JSON)
* A **FastAPI** backend for RESTful API access
* A **Streamlit** frontend for interactive exploration

> Ideal for researchers, journalists, analysts, or developers interested in media monitoring, multilingual sentiment trends, or news aggregation.

---

## 🚀 Features

### 🔍 Core Functionality

* **Multi-country RSS Scraping**: 30+ sources (BBC, Al Jazeera, NHK, CNN, etc.) across 25+ countries using `feedparser`
* **Historical Data Parsing**: Scrapes older articles with `BeautifulSoup4`
* **Structured Data Extraction**: Fields include:

  * `Title`, `Published Date`, `Source`, `Country`, `Summary`, `URL`, `Language`, `Sentiment`
* **Robust Error Handling**: Defaults and fallbacks for missing metadata, encoding errors, and structure mismatches

### 🧠 Intelligence

* **Language Detection**: `langdetect` identifies the article language (e.g., `en`, `hi`, `ja`)
* **Sentiment Analysis**: Classifies article summaries as `positive`, `negative`, or `neutral` using `vaderSentiment`

### 💾 Data Storage

* **SQLite Database**: `news_data.db` with unique constraints to prevent duplicates
* **CSV & JSON** Exports: Stored in the `/downloads` directory for easy access and portability

### 🌐 API with FastAPI

* RESTful endpoints for querying, filtering, and scraping news dynamically

### 📊 Streamlit Frontend

* Interactive UI with filters for:

  * Country, Language, Source, Sentiment, Year, Keywords
* Visualizations via `Plotly`
* Live scraping of new feeds
* Export filtered results as CSV/JSON

### ⏰ Automated Scraping

* Every 4 hours using `apscheduler`
* Parallel feed scraping using `concurrent.futures`

---

## 🧩 Architecture Overview

```bash
project_directory/
├── app.py               # FastAPI backend
├── ui_app.py            # Streamlit frontend
├── news_data.db         # SQLite DB
├── downloads/           # Output directory
│   ├── news_data.csv
│   ├── news_data.json
├── news_scraper.log     # Log of scraping events
```

---

## 📡 API Endpoints

| Endpoint           | Method | Description                                            |
| ------------------ | ------ | ------------------------------------------------------ |
| `/news`            | `GET`  | Retrieve all articles                                  |
| `/news/filter`     | `POST` | Filter by country, language, sentiment, year, keywords |
| `/news/scrape`     | `POST` | Scrape custom RSS feed                                 |
| `/news/scrape_all` | `GET`  | Scrape all configured feeds                            |
| `/news/countries`  | `GET`  | List unique countries                                  |
| `/news/sources`    | `GET`  | List news sources                                      |
| `/news/languages`  | `GET`  | List languages                                         |
| `/news/sentiments` | `GET`  | List sentiment labels                                  |
| `/news/years`      | `GET`  | List publication years                                 |

---

## 🔧 Installation

### 🔁 Prerequisites

* Python 3.8+
* Internet connection

### 📦 Install Dependencies

```bash
pip install feedparser pandas requests beautifulsoup4 langdetect vaderSentiment fastapi uvicorn streamlit plotly apscheduler
```

(Optional)

```bash
pip freeze > requirements.txt
```

---

## 🛠️ How to Run

### 1. Start the Backend (FastAPI)

```bash
python app.py
```

* Starts server on `http://localhost:8000`
* Performs initial full scrape and stores data
* Triggers automatic scraping every 4 hours

### 2. Launch the Frontend (Streamlit)

```bash
streamlit run ui_app.py
```

* Opens UI in browser (`http://localhost:8501`)
* Explore, filter, visualize, and export data

---

## 📈 Sample Coverage

| Country      | Sources           | Articles | Historical Coverage |
| ------------ | ----------------- | -------- | ------------------- |
| UK           | BBC, The Guardian | \~50     | Since 2023          |
| USA          | CNN, NY Times     | \~80     | Since 2023          |
| Japan        | NHK, Japan Times  | \~30     | Since 2025          |
| India        | TOI, The Hindu    | \~40     | Since 2025          |
| Germany      | Deutsche Welle    | \~25     | Since 2025          |
| Qatar        | Al Jazeera        | \~20     | Since 2025          |
| Russia       | RT                | \~30     | Since 2025          |
| South Africa | News24            | \~15     | Since 2025          |
| ...          | ...               | ...      | ...                 |

> *Numbers vary based on feed updates and scraping frequency*

---

## 🐛 Troubleshooting

| Issue                                           | Solution                                                 |
| ----------------------------------------------- | -------------------------------------------------------- |
| Backend not starting                            | Check dependencies & logs in `news_scraper.log`          |
| Streamlit shows "No Data"                       | Ensure backend is running and `news_data.db` has entries |
| Language detection only shows "en" or "unknown" | Reset DB and trigger a full scrape                       |
| Invalid RSS feed URL                            | Ensure it ends with `.rss` or `.xml`                     |
| Encoding problems                               | Handled with `.encode('utf-8', errors='ignore')`         |

---

## 🖼️ Screenshots

(Add your screenshots here under `screenshots/` folder)

* Filter Panel
* Article Cards
* Data Visualizations
* Scrape via RSS Form

---

## 🛣️ Roadmap (Planned Enhancements)

* [ ] Add more countries and RSS sources
* [ ] Smarter keyword filtering and full-text search
* [ ] Date range filtering
* [ ] User authentication & dashboards
* [ ] Enhanced visualizations (e.g., heatmaps, trends over time)


---

## 👨‍💻 About the Project

Developed as a comprehensive solution for multilingual news scraping and exploration. Demonstrates skills in:

* Web scraping (RSS + HTML)
* Natural Language Processing
* API development
* Data engineering and visualization
* Full-stack application integration

---

## 📚 References & Docs

* [FastAPI Docs](https://fastapi.tiangolo.com/)
* [Streamlit Docs](https://docs.streamlit.io/)
* [Feedparser Docs](https://pythonhosted.org/feedparser/)
* [BeautifulSoup4 Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Langdetect](https://pypi.org/project/langdetect/)
* [VADER Sentiment](https://github.com/cjhutto/vaderSentiment)

---

## 📄 License

© 2025 **News Explorer**. All rights reserved.
