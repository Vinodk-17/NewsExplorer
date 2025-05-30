import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="News Explorer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_URL = "http://localhost:8000"

# Language code to name mapping
LANGUAGE_MAP = {
    'en': 'English',
    'hi': 'Hindi',
    'ar': 'Japanese',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'it': 'Italian',
    'ko': 'Korean',
    'tr': 'Turkish',
    'id': 'Indonesian',
    'ms': 'Malay',
    'unknown': 'Unknown'
}

# Reverse mapping for sending to backend
REVERSE_LANGUAGE_MAP = {v: k for k, v in LANGUAGE_MAP.items()}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(endpoint, params=None):
    """Fetch data from the API."""
    try:
        response = requests.get(f"{API_URL}/{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching {endpoint}: {e}. Is the backend running at {API_URL}?")
        return []

@st.cache_data(ttl=3600)  # Cache for 1 hour
def post_data(endpoint, data):
    """Post data to the API."""
    try:
        response = requests.post(f"{API_URL}/{endpoint}", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error posting to {endpoint}: {e}. Is the backend running at {API_URL}?")
        return []

def main():
    st.title("📰 News Explorer")
    st.markdown("Explore news articles from different countries collected from various sources.")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        countries = sorted(fetch_data("news/countries"))
        sources = sorted(fetch_data("news/sources"))
        languages = sorted(fetch_data("news/languages"))
        sentiments = ['positive', 'negative', 'neutral', 'unknown']
        years = sorted(fetch_data("news/years"), reverse=True)

        selected_countries = st.multiselect(
            "Select Countries",
            countries,
            default=None,
            help="Filter by country"
        )
        selected_sources = st.multiselect(
            "Select Sources",
            sources,
            default=None,
            help="Filter by news source"
        )
        # Display human-readable language names
        selected_languages = st.multiselect(
            "Select Languages",
            [LANGUAGE_MAP.get(lang, lang) for lang in languages],
            default=None,
            help="Filter by language"
        )
        selected_sentiments = st.multiselect(
            "Select Sentiments",
            sentiments,
            default=None,
            help="Filter by sentiment"
        )
        selected_years = st.text_input(
            "Years (comma-separated, e.g., 2023,2024)",
            "",
            help="Filter by publication year"
        )
        keyword = st.text_input(
            "Keyword (in title or summary)",
            "",
            help="Search in titles or summaries"
        )
        apply_filters = st.button("Apply Filters")

    # Initialize session state to track the active dataset
    if 'active_data' not in st.session_state:
        st.session_state.active_data = None
        st.session_state.data_df = pd.DataFrame()

    # Main content
    st.subheader("News Articles")
    if apply_filters or not (selected_countries or selected_sources or selected_languages or selected_sentiments or selected_years or keyword):
        # Prepare filter params, converting language names back to codes
        filters = {
            'country': ','.join(selected_countries) if selected_countries else None,
            'source': ','.join(selected_sources) if selected_sources else None,
            'language': ','.join([REVERSE_LANGUAGE_MAP.get(lang, lang) for lang in selected_languages]) if selected_languages else None,
            'sentiment': ','.join(selected_sentiments) if selected_sentiments else None,
            'year': selected_years.strip() if selected_years.strip() else None,
            'keyword': keyword.strip() if keyword.strip() else None
        }
        news_data = post_data("news/filter", filters)
        filtered_df = pd.DataFrame(news_data)
        if not filtered_df.empty:
            st.session_state.active_data = 'filtered'
            st.session_state.data_df = filtered_df
            st.write(f"Total articles found: {len(filtered_df)}")
            # Display as expandable cards
            for _, row in filtered_df.iterrows():
                with st.expander(f"{row.get('title', 'No title')}"):
                    url = row.get('url', 'No URL available')
                    st.markdown(f"**Link to full Article:** [{'Click here' if url != 'No URL available' else url}]({url})")
                    st.markdown(f"**News Title:** {row.get('title', 'N/A')}")
                    st.markdown(f"**Publication Date:** {row.get('publication_date', 'N/A')}")
                    st.markdown(f"**Source (News Agency):** {row.get('source', 'N/A')}")
                    st.markdown(f"**Country:** {row.get('country', 'N/A')}")
                    st.markdown(f"**Language:** {LANGUAGE_MAP.get(row.get('language', 'N/A'), row.get('language', 'N/A'))}")
                    st.markdown(f"**Sentiment:** {row.get('sentiment', 'N/A')}")
                    st.markdown(f"**Summary:** {row.get('summary', 'No summary available')}")
        else:
            st.warning("No articles found with the current filters")
            st.session_state.active_data = None
            st.session_state.data_df = pd.DataFrame()

    # Visualizations
    st.subheader("Visualizations")
    col1, col2, col3 = st.columns(3)
    with col1:
        if not st.session_state.data_df.empty and st.session_state.active_data == 'filtered':
            country_counts = st.session_state.data_df['country'].value_counts().reset_index()
            country_counts.columns = ['Country', 'Count']
            fig = px.bar(country_counts, x='Country', y='Count', title='Articles by Country')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data for Articles by Country")
    with col2:
        if not st.session_state.data_df.empty and st.session_state.active_data == 'filtered':
            language_counts = st.session_state.data_df['language'].value_counts().reset_index()
            language_counts.columns = ['Language', 'Count']
            # Map language codes to names for visualization
            language_counts['Language'] = language_counts['Language'].map(lambda x: LANGUAGE_MAP.get(x, x))
            fig = px.pie(language_counts, names='Language', values='Count', title='Articles by Language')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data for Articles by Language")
    with col3:
        if not st.session_state.data_df.empty and st.session_state.active_data == 'filtered':
            sentiment_counts = st.session_state.data_df['sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Count']
            fig = px.bar(sentiment_counts, x='Sentiment', y='Count', title='Sentiment Distribution')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data for Sentiment Distribution")

    # Live scraping
    st.subheader("Scrape News Feed Using Url")
    with st.form("scrape_form"):
        rss_url = st.text_input("Enter RSS Feed URL")
        custom_country = st.text_input("Country (optional)", value="Custom")
        custom_agency = st.text_input("Agency (optional)", value="Custom Feed")
        submit_button = st.form_submit_button("Scrape Now")

        if submit_button and rss_url:
            with st.spinner("Scraping RSS feed..."):
                scrape_data = {
                    "rss_url": rss_url,
                    "country": custom_country,
                    "agency": custom_agency
                }
                scraped_data = post_data("news/scrape", scrape_data)
                if scraped_data:
                    st.session_state.active_data = 'scraped'
                    st.session_state.data_df = pd.DataFrame(scraped_data)
                    st.success(f"Scraped {len(scraped_data)} articles")
                    # Map language codes to names for display
                    display_df = st.session_state.data_df.copy()
                    display_df['language'] = display_df['language'].map(lambda x: LANGUAGE_MAP.get(x, x))
                    st.dataframe(display_df)
                else:
                    st.error("No articles found or invalid RSS feed")
                    st.session_state.active_data = None
                    st.session_state.data_df = pd.DataFrame()

    # Common download options
    st.subheader("Download Data")
    if not st.session_state.data_df.empty:
        data_type = "Filtered" if st.session_state.active_data == 'filtered' else "Scraped"
        st.write(f"Downloading {data_type} data: {len(st.session_state.data_df)} articles")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label=f"Download {data_type} CSV",
                data=st.session_state.data_df.to_csv(index=False),
                file_name=f"{st.session_state.active_data}_news.csv",
                mime="text/csv",
                key=f"{st.session_state.active_data}_csv"
            )
        with col2:
            st.download_button(
                label=f"Download {data_type} JSON",
                data=json.dumps(st.session_state.data_df.to_dict('records'), ensure_ascii=False),
                file_name=f"{st.session_state.active_data}_news.json",
                mime="application/json",
                key=f"{st.session_state.active_data}_json"
            )
    else:
        st.write("No data available to download")

    # Summary section
    st.divider()
    st.subheader("Available Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Countries")
        countries = fetch_data("news/countries")
        if countries:
            st.write(f"Total countries: {len(countries)}")
            st.dataframe(pd.DataFrame(countries, columns=["Country"]), height=200)
        else:
            st.warning("No countries data available")
    with col2:
        st.markdown("### Sources")
        sources = fetch_data("news/sources")
        if sources:
            st.write(f"Total sources: {len(sources)}")
            st.dataframe(pd.DataFrame(sources, columns=["Source"]), height=200)
        else:
            st.warning("No sources data available")
    with col3:
        st.markdown("### Languages")
        languages = fetch_data("news/languages")
        if languages:
            st.write(f"Total languages: {len(languages)}")
            # Display language names in summary
            st.dataframe(pd.DataFrame([LANGUAGE_MAP.get(lang, lang) for lang in languages], columns=["Language"]), height=200)
        else:
            st.warning("No languages data available")

if __name__ == "__main__":
    main()