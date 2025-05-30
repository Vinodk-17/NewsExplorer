
# News Explorer

**Web Scraping and Data Extraction of News from Multiple Countries Using RSS Feeds**

## Overview

 News Explorer is a Python-based project that scrapes news articles from RSS feeds and historical URLs across 25+ countries. It extracts structured data, detects article languages, performs sentiment analysis, and stores the results in a SQLite database and CSV and JSON files. The project includes a FastAPI backend for serving data and a Streamlit frontend for interactive exploration of news articles.

This project fulfills the following core requirements:
- Scrapes news from 25+ countries using RSS feeds.
- Parses RSS feeds with `feedparser` and historical articles with `BeautifulSoup4`.
- Handles missing data, encoding issues, and errors gracefully.
- Stores data in SQLite, CSV, and JSON formats.
- Provides a RESTful API via FastAPI.
- Detects article languages using `langdetect`.
- Analyzes sentiment using `vaderSentiment`.
- Offers a user-friendly Streamlit UI for filtering and visualizing news data.

## Features

### Core Features
- **RSS Feed Scraping**:
  - Uses `feedparser` to scrape news from 24+ countries and 30+ news agencies (e.g., BBC, Al Jazeera, NHK).
  - Filters articles to include only those from the last 365 days.
- **Historical Article Parsing**:
  - Scrapes older articles from specified URLs using `BeautifulSoup4`.
  - Extracts metadata like title, summary, and publication date.
- **Data Extraction**:
  - Captures fields: Title, Publication Date, Source, Country, Summary, URL, Language, Sentiment.
  - Handles missing data with defaults (e.g., "No Title", "Unknown").
- **Data Storage**:
  - Stores articles in a SQLite database (`news_data.db`) with unique constraints.
  - Saves data to CSV (`news_data.csv`) and JSON (`news_data.json`) files in the `downloads` directory.
- **Language Detection**:
  - Detects article languages (e.g., 'en', 'hi', 'ja') using `langdetect`.
- **Sentiment Analysis**:
  - Analyzes article summaries using `vaderSentiment` to classify sentiment as positive, negative, or neutral.

### Bonus Features
- **FastAPI Backend**:
  - Serves data via REST endpoints for fetching, filtering, and scraping news.
- **Streamlit Frontend**:
  - Interactive UI for filtering news by country, source, language, sentiment, year, and keyword.
  - Visualizes data with Plotly charts (e.g., articles by country, language, sentiment).
  - Supports live scraping of new RSS feeds and downloading filtered/scraped data as CSV/JSON.
- **Scheduled Scraping**:
  - Uses `apscheduler` to automatically scrape all feeds every 4 hours.

## Libraries Used

- `feedparser`: Parse RSS feeds.
- `pandas`: Data manipulation and storage.
- `sqlite3`: SQLite database management.
- `requests`: HTTP requests for scraping.
- `beautifulsoup4`: HTML parsing for historical articles.
- `langdetect`: Language detection.
- `vaderSentiment`: Sentiment analysis.
- `fastapi`: REST API framework.
- `uvicorn`: ASGI server for FastAPI.
- `streamlit`: Frontend UI framework.
- `plotly`: Data visualization.
- `apscheduler`: Scheduled tasks.
- `concurrent.futures`: Parallel feed scraping.

## API Endpoints

The FastAPI backend provides the following endpoints:

- **GET `/news`**:
  - Returns all news articles from the database.
- **POST `/news/filter`**:
  - Filters articles by country, source, language, sentiment, year, and/or keyword.
  - Example payload: `{"country": "India,UK", "language": "en,hi", "keyword": "politics"}`
- **GET `/news/countries`**:
  - Lists all unique countries in the database.
- **GET `/news/sources`**:
  - Lists all unique news sources.
- **GET `/news/languages`**:
  - Lists all detected languages.
- **GET `/news/sentiments`**:
  - Lists all unique sentiment labels.
- **GET `/news/years`**:
  - Lists all unique publication years.
- **POST `/news/scrape`**:
  - Scrapes a single RSS feed.
  - Example payload: `{"rss_url": "https://example.com/rss", "country": "Custom", "agency": "Custom Feed"}`
- **GET `/news/scrape_all`**:
  - Triggers a full scrape of all configured feeds and historical articles.

## Sample Data Summary

| Country       | News Agencies                | Total Articles | Historical Data |
|---------------|------------------------------|----------------|-----------------|
| UK            | BBC News, The Guardian       | ~50            | Since 2023      |
| USA           | CNN, The New York Times      | ~80            | Since 2023      |
| Japan         | NHK, The Japan Times         | ~30            | 2025            |
| India         | The Times of India, The Hindu| ~40            | 2025            |
| Qatar         | Al Jazeera                   | ~20            | 2025            |
| Germany       | Deutsche Welle               | ~25            | 2025            |
| France        | France 24                    | ~20            | 2025            |
| Brazil        | Folha de S.Paulo             | ~15            | 2025            |
| Russia        | RT                           | ~30            | 2025            |
| South Africa  | News24                       | ~15            | 2025            |

*Note*: Article counts depend on feed availability and scraping frequency.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
- **Internet Connection**: Required for scraping RSS feeds and historical URLs.

## How to Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install feedparser pandas sqlite3 requests beautifulsoup4 langdetect vaderSentiment fastapi uvicorn streamlit plotly apscheduler
```

*Note*: This assumes you are running directly in your global Python environment, as per your request to avoid using a virtual environment.

## How to Run the Project

### Step 1: Run the Backend

1. Save the backend code as `app.py`.
2. Open a terminal in the directory containing `app.py`.
3. Run the FastAPI server:
   ```bash
   python app.py
   ```
4. The backend will:
   - Perform an initial scrape of all RSS feeds and historical URLs.
   - Save data to `news_data.db`, `downloads/news_data.csv`, and `downloads/news_data.json`.
   - Start a server at `http://localhost:8000`.
   - Schedule scraping every 4 hours.

### Step 2: Run the Frontend

1. Save the frontend code as `ui_app.py`.
2. Open a new terminal in the directory containing `ui_app.py`.
3. Run the Streamlit app:
   ```bash
   streamlit run ui_app.py
   ```
4. The Streamlit UI will open in your default browser (typically at `http://localhost:8501`).

### Step 3: Explore the Application

- **Backend API**:
  - Access API endpoints via `http://localhost:8000` (e.g., `http://localhost:8000/news`).
  - Use tools like `curl`, Postman, or the Streamlit UI to interact with the API.
- **Frontend UI**:
  - Filter news articles by country, source, language, sentiment, year, or keyword.
  - Visualize data with charts (articles by country, language, sentiment).
  - Scrape new RSS feeds using the "Scrape News Feed Using Url" form.
  - Download filtered or scraped data as CSV or JSON.

## Directory Structure

After running the project, the following files and directories will be created:

```
project_directory/
├── app.py                # Backend FastAPI script
├── ui_app.py             # Frontend Streamlit script
├── news_data.db          # SQLite database
├── downloads/            # Output directory
│   ├── news_data.csv     # Scraped data in CSV format
│   ├── news_data.json    # Scraped data in JSON format
├── news_scraper.log      # Log file for scraping events and errors
```

## Issues Encountered and Resolutions

1. **Inconsistent RSS Feed Structures**:
   - Some feeds lack fields like `summary` or `published`. Handled using `entry.get()` with defaults.
. **Historical Article Parsing**:
   - Missing metadata (e.g., publication date) in some articles. Used fallback strategies like meta tags and current timestamp.
4. **Language Detection**:
   - Short texts caused unreliable detection. Set a minimum length (10 characters) and fallback to 'unknown'.
5. **Encoding Issues**:
   - Non-UTF-8 characters in feeds/articles. Handled with `encode('utf-8', errors='ignore')`.

## Screenshots

*Note*: Add screenshots of the Streamlit UI (e.g., filter panel, article cards, visualizations) to enhance the README. Below are placeholders for where images would go:

- **Filter Panel**:
  ![Filter Panel](screenshots/filter_panel.png)
- **Article Cards**:
  ![Article Cards](screenshots/article_cards.png)
- **Visualizations**:
  ![Visualizations](screenshots/visualizations.png)
- **Live Scraping**:
  ![Live Scraping](screenshots/live_scraping.png)

## Troubleshooting

- **Backend Fails to Start**:
  - Ensure all dependencies are installed (`pip install -r requirements.txt`).
  - Check `news_scraper.log` for errors (e.g., network issues, invalid RSS URLs).
- **Frontend Shows "No Data"**:
  - Verify the backend is running at `http://localhost:8000`.
  - Clear the Streamlit cache: `streamlit cache clear`.
  - Ensure the database (`news_data.db`) contains data. If empty, trigger a scrape via `/news/scrape_all`.
- **Language Detection Issues**:
  - If only 'en' or 'unknown' appears, reset the database (`rm news_data.db`) and rerun the backend to scrape fresh data.
- **Invalid RSS Feed**:
  - When scraping a new feed, ensure the URL is a valid RSS feed (e.g., ends with `.xml` or `.rss`).

## Future Improvements

- Add more RSS feeds for additional countries.
- Enhance historical article parsing with deeper content extraction.
- Implement advanced filtering (e.g., date ranges, multiple keywords).
- Add user authentication for the API.
- Improve visualization options (e.g., time-series charts).

## About

This project was developed to scrape and analyze global news articles, providing an interactive interface for exploring news data. It demonstrates web scraping, API development, and data visualization techniques.

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Feedparser Documentation](https://feedparser.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Langdetect Documentation](https://pypi.org/project/langdetect/)

## License

© 2025 Global News Explorer. All rights reserved.

---

### Notes
- **No Virtual Environment**: The README assumes direct execution in the global Python environment, as requested. Users must ensure dependencies are installed globally.
- **Screenshots**: The README includes placeholders for screenshots. You can capture images of the Streamlit UI (e.g., filter panel, visualizations) and place them in a `screenshots/` directory.
- **Requirements File**: If you want to include a `requirements.txt`, you can generate it with:
  ```bash
  pip freeze > requirements.txt
  ```
  Then reference it in the "How to Install Dependencies" section.
- **Customization**: If you need specific sections added (e.g., deployment instructions, contributor guidelines), let me know!

This README should provide clear guidance for running your project and understanding its functionality. If you need further refinements or additional sections, feel free to ask!