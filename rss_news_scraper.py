import streamlit as st
import feedparser
import pandas as pd
import datetime
import json
from io import StringIO

st.set_page_config(page_title="RSS News Scraper", layout="wide")

st.title("📰 RSS News Feed Scraper")
st.markdown("Enter the RSS feed URL below and get the latest news in a structured table.")

# Input field for RSS URL
rss_url = st.text_input("Enter RSS Feed URL", placeholder="e.g., http://feeds.bbci.co.uk/news/rss.xml")

@st.cache_data(show_spinner=False)
def parse_rss_feed(url):
    feed = feedparser.parse(url)
    data = []
    for entry in feed.entries:
        data.append({
            "Title": entry.get("title", "N/A"),
            "Published": entry.get("published", "N/A"),
            "Summary": entry.get("summary", "N/A"),
            "Link": entry.get("link", "N/A"),
            "Source": feed.feed.get("title", "Unknown Source"),
            "Country": detect_country_from_url(url)
        })
    return pd.DataFrame(data)

def detect_country_from_url(url):
    if "bbc" in url:
        return "UK"
    elif "cnn" in url:
        return "USA"
    elif "aljazeera" in url:
        return "Middle East"
    elif "nhk" in url:
        return "Japan"
    else:
        return "Unknown"

if rss_url:
    try:
        df = parse_rss_feed(rss_url)
        if df.empty:
            st.warning("No data found. Please check the RSS URL.")
        else:
            st.success(f"Fetched {len(df)} articles from {df['Source'].iloc[0]}")
            st.dataframe(df, use_container_width=True)

            # Download options
            col1, col2 = st.columns(2)

            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name='rss_news_data.csv',
                    mime='text/csv',
                )

            with col2:
                json_data = df.to_json(orient="records", indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_data,
                    file_name='rss_news_data.json',
                    mime='application/json',
                )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
