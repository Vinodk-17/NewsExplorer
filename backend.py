import feedparser
import pandas as pd
import sqlite3
import requests
import time
from datetime import datetime, timedelta
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import os
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from apscheduler.schedulers.background import BackgroundScheduler
import json
from langdetect import detect, DetectorFactory

# Ensure consistent language detection results by setting a fixed seed
DetectorFactory.seed = 0

# Configure logging to record events and errors to a file
logging.basicConfig(
    filename='news_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Dictionary of RSS feeds organized by country, with agency names and URLs
RSS_FEEDS = {
    'UK': [
        ('BBC News', 'http://feeds.bbci.co.uk/news/rss.xml'),
        ('The Guardian', 'https://www.theguardian.com/world/rss'),
    ],
    'USA': [
        ('CNN', 'http://rss.cnn.com/rss/edition.rss'),
        ('The New York Times', 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'),
    ],
    'Qatar': [
        ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
    ],
    'Japan': [
        ('NHK', 'https://www3.nhk.or.jp/rss/news/cat0.xml'),
        ('The Japan Times', 'https://www.japantimes.co.jp/feed/top'),
    ],
    'India': [
        ('The Times of India', 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'),
        ('The Hindu', 'https://www.thehindu.com/feeder/default.rss'),
    ],
    'Singapore': [
        ('The Straits Times', 'https://www.straitstimes.com/rss/latest-news'),
    ],
    'Malaysia': [
        ('The Star', 'https://www.thestar.com.my/rss'),
    ],
    'Indonesia': [
        ('Jakarta Post', 'https://www.thejakartapost.com/feed'),
    ],
    'South Korea': [
        ('The Korea Herald', 'http://www.koreaherald.com/rss'),
    ],
    'China': [
        ('China Daily', 'http://www.chinadaily.com.cn/rss/world_rss.xml'),
    ],
    'Australia': [
        ('ABC News', 'https://www.abc.net.au/news/feed'),
    ],
    'Canada': [
        ('CBC News', 'https://www.cbc.ca/webfeed/rss/rss-world'),
    ],
    'Germany': [
        ('Deutsche Welle', 'https://rss.dw.com/xml/rss_en_world'),
    ],
    'France': [
        ('France 24', 'https://www.france24.com/en/rss'),
    ],
    'Brazil': [
        ('Folha de S.Paulo', 'https://www1.folha.uol.com.br/internacional/en/rss102.xml'),
    ],
    'South Africa': [
        ('News24', 'https://www.news24.com/news24/rss'),
    ],
    'Russia': [
        ('RT', 'https://www.rt.com/rss/news'),
    ],
    'Nigeria': [
        ('The Punch', 'https://punchng.com/feed'),
    ],
    'Mexico': [
        ('El Universal', 'https://www.eluniversal.com.mx/rss.xml'),
    ],
    'Italy': [
        ('ANSA', 'https://www.ansa.it/sito/ansait_rss.xml'),
    ],
    'Spain': [
        ('El País', 'https://feeds.elpais.com/rss'),
    ],
    'Turkey': [
        ('Hurriyet Daily News', 'http://www.hurriyetdailynews.com/rss'),
    ],
    'Egypt': [
        ('Ahram Online', 'http://english.ahram.org.eg/RSS.aspx'),
    ],
    'Argentina': [
        ('La Nacional', 'https://www.lanacion.com.ar/rss/arcio/rss/'),
    ],
}

# Dictionary of historical article URLs for specific countries
HISTORICAL_URLS = {
    'UK': [
        'https://www.bbc.com/news/articles/cp00jze920eo',
    ],
    'USA': [
        'https://www.cnn.com/2023/01/31/tennis/atp-alexander-zverev-domestic-abuse-spt-intl/index.html',
    ],
    'India': [
        'https://timesofindia.indiatimes.com/toi/articleshow/121320973.cms',
    ],
    'Qatar': [
        'https://www.aljazeera.com/news/liveblog/2025/5/30/live-israel-forces-new-displacement-in-north-gaza-as-strikes-intensify',
    ],
}

# Initialize FastAPI application
app = FastAPI()

# Pydantic model for RSS feed scrape request
class ScrapeRequest(BaseModel):
    rss_url: str  # URL of the RSS feed to scrape
    country: str = "Custom"  # Country of the feed (default: Custom)
    agency: str = "Custom Feed"  # Agency name (default: Custom Feed)

# Pydantic model for news filtering request
class FilterRequest(BaseModel):
    country: str | None = None  # Filter by country (optional)
    source: str | None = None  # Filter by source (optional)
    language: str | None = None  # Filter by language (optional)
    sentiment: str | None = None  # Filter by sentiment (optional)
    year: str | None = None  # Filter by year (optional)
    keyword: str | None = None  # Filter by keyword in title/summary (optional)

class NewsScraper:
    """Class to manage news scraping, storage, and processing."""
    
    def __init__(self, db_name='news_data.db', output_dir='downloads'):
        """Initialize the NewsScraper with database and output directory settings.
        
        Args:
            db_name (str): Name of the SQLite database file (default: 'news_data.db').
            output_dir (str): Directory to save output files (default: 'downloads').
        """
        self.db_name = db_name
        self.output_dir = output_dir
        self.create_output_directory()
        self.setup_database()
        self.news_data = []  # List to store scraped articles
        self.session = self.setup_session()
        self.analyzer = SentimentIntensityAnalyzer()  # Initialize sentiment analyzer
        self.scheduler = BackgroundScheduler()  # Initialize background scheduler
        self.setup_scheduler()

    def create_output_directory(self):
        """Create the output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logging.info(f"Created output directory: {self.output_dir}")

    def setup_database(self):
        """Set up the SQLite database with a news table."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news (
                        title TEXT,
                        publication_date TEXT,
                        source TEXT,
                        country TEXT,
                        summary TEXT,
                        url TEXT,
                        language TEXT NOT NULL,
                        sentiment TEXT,
                        UNIQUE(title, publication_date, source, url)
                    )
                ''')
                conn.commit()
            logging.info("Database setup completed")
        except sqlite3.Error as e:
            logging.error(f"Database setup error: {str(e)}")

    def setup_session(self):
        """Set up an HTTP session with retry mechanism for scraping.
        
        Returns:
            requests.Session: Configured session with retries.
        """
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def clean_text(self, text):
        """Clean text by removing extra whitespace and handling encoding issues.
        
        Args:
            text (str): Input text to clean.
            
        Returns:
            str: Cleaned text.
        """
        if not text:
            return ""
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned.encode('utf-8', errors='ignore').decode('utf-8')

    def detect_language(self, text):
        """Detect the language of the provided text using langdetect.
        
        Args:
            text (str): Text to analyze for language detection.
            
        Returns:
            str: Language code (e.g., 'en', 'hi') or 'unknown' if detection fails.
        """
        try:
            if len(text.strip()) < 10:
                return 'unknown'
            lang = detect(text[:1000])  # Limit to first 1000 characters
            return lang if lang else 'unknown'
        except Exception as e:
            logging.error(f"Language detection error: {str(e)}")
            return 'unknown'

    def analyze_sentiment(self, text):
        """Analyze the sentiment of the provided text using VADER.
        
        Args:
            text (str): Text to analyze for sentiment.
            
        Returns:
            str: Sentiment label ('positive', 'negative', 'neutral', or 'unknown').
        """
        try:
            scores = self.analyzer.polarity_scores(text)
            compound = scores['compound']
            if compound > 0.05:
                return 'positive'
            elif compound < -0.05:
                return 'negative'
            else:
                return 'neutral'
        except Exception as e:
            logging.error(f"Sentiment analysis error: {str(e)}")
            return 'unknown'

    def fetch_feed(self, country, agency, feed_url):
        """Fetch and parse articles from an RSS feed.
        
        Args:
            country (str): Country associated with the feed.
            agency (str): News agency name.
            feed_url (str): URL of the RSS feed.
            
        Returns:
            list: List of article dictionaries with title, date, source, etc.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = self.session.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            if not feed.entries:
                logging.warning(f"No entries found for {agency} ({country})")
                return []

            entries = []
            one_year_ago = datetime.now() - timedelta(days=365)

            for entry in feed.entries:
                try:
                    pub_date = entry.get('published', entry.get('updated', ''))
                    if pub_date:
                        try:
                            pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                            if pub_date < one_year_ago:
                                continue
                        except ValueError:
                            pub_date = datetime.now()
                    else:
                        pub_date = datetime.now()
                except Exception as e:
                    logging.error(f"Error parsing date for {entry.get('title', 'No title')}: {str(e)}")
                    pub_date = datetime.now()

                title = self.clean_text(entry.get('title', 'No Title'))
                summary = self.clean_text(entry.get('summary', entry.get('description', '')))
                url = entry.get('link', '')
                language = self.detect_language(title + ' ' + summary)
                sentiment = self.analyze_sentiment(summary)

                entries.append({
                    'title': title,
                    'publication_date': pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'source': agency,
                    'country': country,
                    'summary': summary,
                    'url': url,
                    'language': language,
                    'sentiment': sentiment
                })

            logging.info(f"Fetched {len(entries)} articles from {agency} ({country})")
            return entries

        except requests.RequestException as e:
            logging.error(f"Failed to fetch {feed_url} for {agency} ({country}): {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error processing {feed_url} for {agency} ({country}): {str(e)}")
            return []

    def scrape_historical_articles(self, historical_urls):
        """Scrape articles from historical URLs.
        
        Args:
            historical_urls (dict): Dictionary of URLs by country.
            
        Returns:
            list: List of article dictionaries with scraped metadata.
        """
        headers = {'User-Agent': 'Mozilla/5.0'}
        entries = []

        for country, urls in historical_urls.items():
            for url in urls:
                try:
                    response = self.session.get(url, headers=headers, timeout=10)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.text, 'summary')

                    title = self.clean_text(soup.find('title').text if soup.find('title') else 'No Title')
                    summary = self.clean_text(' '.join(p.text for p in soup.find_all('p')[:3]) if soup.find_all('p') else '')
                    pub_date = soup.find('meta', property='article:published_time')
                    pub_date = pub_date['content'] if pub_date and pub_date.get('content') else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    source = soup.find('meta', property='og_site')
                    source = source['content'] if source and source.get('content') else 'Unknown'
                    language = self.detect_language(title + ' ' + summary)
                    sentiment = self.analyze_sentiment(summary)

                    entries.append({
                        'title': title,
                        'publication_date': pub_date,
                        'source': source,
                        'country': country,
                        'summary': summary,
                        'url': url,
                        'language': language,
                        'sentiment': sentiment
                    })
                except Exception as e:
                    logging.error(f"Historical scrape error for {url}: {str(e)}")
                    continue
        return entries

    def scrape_all_feeds(self):
        """Scrape all configured RSS feeds and historical articles."""
        tasks = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for country, feeds in RSS_FEEDS.items():
                for agency, feed_url in feeds:
                    tasks.append(executor.submit(self.fetch_feed, country, agency, feed_url))
            self.news_data.extend(self.scrape_historical_articles(HISTORICAL_URLS))
            for future in tasks:
                self.news_data.extend(future.result())
        logging.info(f"Total articles fetched: {len(self.news_data)}")

    def scrape_single_feed(self, feed_url, country='Custom', agency='Custom Feed'):
        """Scrape a single RSS feed and save results.
        
        Args:
            feed_url (str): URL of the RSS feed.
            country (str, optional): Country of the feed. Defaults to 'Custom'.
            agency (str, optional): Agency name. Defaults to 'Custom Feed'.
            
        Returns:
            list: List of scraped article dictionaries.
        """
        entries = self.fetch_feed(country, agency, feed_url)
        self.news_data.extend(entries)
        self.save_to_database()
        self.save_to_csv()
        self.save_to_json()
        return entries

    def remove_duplicates(self):
        """Remove duplicate articles based on title, source, and URL."""
        df = pd.DataFrame(self.news_data)
        initial_count = len(df)
        df = df.drop_duplicates(subset=['title', 'source', 'url'], keep='first')
        self.news_data = df.to_dict('records')
        logging.info(f"Removed {initial_count - len(self.news_data)} duplicates")

    def save_to_csv(self):
        """Save scraped articles to a CSV file."""
        try:
            df = pd.DataFrame(self.news_data)
            output_path = os.path.join(self.output_dir, 'news_data.csv')
            df.to_csv(output_path, index=False, encoding='utf-8')
            logging.info(f"Saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving to CSV: {str(e)}")

    def save_to_json(self):
        """Save scraped articles to a JSON file."""
        try:
            df = pd.DataFrame(self.news_data)
            output_path = os.path.join(self.output_dir, 'news_data.json')
            df.to_json(output_path, orient='records', force_ascii=False)
            logging.info(f"Saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving to JSON: {str(e)}")

    def save_to_database(self):
        """Save scraped articles to the SQLite database."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                for item in self.news_data:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO news (title, publication_date, source, country, summary, url, language, sentiment)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item['title'],
                        item['publication_date'],
                        item['source'],
                        item['country'],
                        item['summary'],
                        item['url'],
                        item['language'],
                        item['sentiment']
                    ))
                    conn.commit()
            logging.info("Saved data to database")
        except sqlite3.Error as e:
            logging.error(f"Error saving to database: {str(e)}")

    def setup_scheduler(self):
        """Set up a background scheduler to run scraping every 4 hours."""
        self.scheduler.add_job(self.run_scrape, 'interval', hours=4)
        self.scheduler.start()
        logging.info("Scheduler started for scraping every 4 hours")

    def run_scrape(self):
        """Run the full scraping process and save results."""
        try:
            self.news_data = []
            self.scrape_all_feeds()
            self.remove_duplicates()
            self.save_to_csv()
            self.save_to_json()
            self.save_to_database()
            logging.info("Scheduled scraping completed")
        except Exception as e:
            logging.error(f"Scheduled scraping failed: {str(e)}")

scraper = NewsScraper()

# API Endpoints
@app.get("/news")
async def get_all_news():
    """Fetch all news articles from the database.
    
    Returns:
        list: List of article dictionaries.
        
    Raises:
        HTTPException: If there's an error accessing the database.
    """
    try:
        with sqlite3.connect(scraper.db_name) as conn:
            df = pd.read_sql_query("SELECT * FROM news", conn)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.post("/news/filter")
async def filter_news(filters: FilterRequest):
    """Filter news articles based on user-specified criteria.
    
    Args:
        filters (FilterRequest): Filter parameters (country, source, etc.).
        
    Returns:
        list: List of filtered article dictionaries.
        
    Raises:
        HTTPException: If there's an error querying the database.
    """
    try:
        query = "SELECT * FROM news WHERE 1=1"
        params = []

        if filters.country:
            countries = [c.strip() for c in filters.country.split(',')]
            query += f" AND country IN ({','.join(['?' for _ in countries])})"
            params.extend(countries)
        if filters.source:
            sources = [s.strip() for s in filters.source.split(',')]
            query += f" AND source IN ({','.join(['?' for _ in sources])})"
            params.extend(sources)
        if filters.language:
            languages = [l.strip() for l in filters.language.split(',')]
            query += f" AND language IN ({','.join(['?' for _ in languages])})"
            params.extend(languages)
        if filters.sentiment:
            sentiments = [s.strip() for s in filters.sentiment.split(',')]
            query += f" AND sentiment IN ({','.join(['?' for _ in sentiments])})"
            params.extend(sentiments)
        if filters.year:
            years = [y.strip() for y in filters.year.split(',')]
            query += f" AND strftime('%Y', publication_date) IN ({','.join(['?' for _ in years])})"
            params.extend(years)
        if filters.keyword:
            query += " AND (title LIKE ? summary LIKE ?)"
            params.extend([f"%{filters.keyword}%", f"%{filters.keyword}%"])

        with sqlite3.connect(scraper.db_name) as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering news: {str(e)}")

@app.get("/news/countries")
async def get_countries():
    """Fetch unique countries from the news database.
    
    Returns:
        list: List of unique country names.
        
    Raises:
        HTTPException: If there's an error accessing the database.
    """
    try:
        with sqlite3.connect(scraper.db_name) as conn:
            cursor = conn.execute('SELECT DISTINCT country FROM news')
            countries = [row[0] for row in cursor.fetchall()]
        return countries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching countries: {str(e)}")

@app.get("/news/sources")
async def get_sources():
    """Fetch unique sources from the news database.
    
    Returns:
        list: List of unique source names.
        
    Raises:
        HTTPException: If there's an error accessing the database.
    """
    try:
        with sqlite3.connect(scraper.db_name) as conn:
            cursor = conn.execute('SELECT DISTINCT source FROM news')
            sources = [row[0] for row in cursor.fetchall()]
        return sources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sources: {str(e)}")

@app.get("/news/languages")
async def get_languages():
    """Fetch unique languages from the news database.
    
    Returns:
        list: List of unique language codes.
        
    Raises:
        HTTPException: If there's an error accessing the database.
    """
    try:
        with sqlite3.connect(scraper.db_name) as conn:
            cursor = conn.execute('SELECT DISTINCT language FROM news')
            languages = [row[0] for row in cursor.fetchall()]
        return languages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching languages: {str(e)}")

@app.get("/news/sentiments")
async def get_sentiments():
    """Fetch unique sentiments from the news database.
    
    Returns:
        list: List of unique sentiment labels.
        
    Raises:
        HTTPException: If there's an error accessing the database.
    """
    try:
        with sqlite3.connect(scraper.db_name) as conn:
            cursor = conn.execute('SELECT DISTINCT sentiment FROM news')
            sentiments = [row[0] for row in cursor.fetchall()]
        return sentiments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sentiments: {str(e)}")

@app.get("/news/years")
async def get_years():
    """Fetch unique years from the news database based on publication date.
    
    Returns:
        list: List of unique years.
        
    Raises:
        HTTPException: If there's an error accessing the database.
    """
    try:
        with sqlite3.connect(scraper.db_name) as conn:
            cursor = conn.execute("SELECT DISTINCT strftime('%Y', publication_date) as year FROM news")
            years = [row[0] for row in cursor.fetchall()]
        return years
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching years: {str(e)}")

@app.post("/news/scrape")
async def scrape_rss(request: ScrapeRequest):
    """Scrape a single RSS feed based on the provided request.
    
    Args:
        request (ScrapeRequest): Request containing RSS URL, country, and agency.
        
    Returns:
        list: List of scraped article dictionaries.
        
    Raises:
        HTTPException: If there's an error during scraping.
    """
    try:
        entries = scraper.scrape_single_feed(request.rss_url, request.country, request.agency)
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping RSS feed: {str(e)}")

@app.get("/news/scrape_all")
async def scrape_all():
    """Trigger a full scrape of all configured feeds and historical articles.
    
    Returns:
        dict: Success message.
        
    Raises:
        HTTPException: If there's an error during scraping.
    """
    try:
        scraper.run_scrape()
        return {"message": "Scraping completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during full scrape: {str(e)}")

if __name__ == "__main__":
    scraper.run_scrape()  # Perform an initial scrape
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Start the FastAPI server