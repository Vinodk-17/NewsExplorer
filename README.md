
# 📰 RSS News Feed Scraper using Streamlit

A powerful Python project to extract and display structured news data from global RSS feeds. Built with **Streamlit**, this tool allows you to paste any RSS feed URL, view the extracted data in a tabular format, and download the results as **CSV** or **JSON**.

---

## 📌 Features

* 🔗 Accepts any valid RSS feed URL
* 📄 Displays real-time scraped news in a table
* 💾 Download scraped data as **CSV** or **JSON**
* 🌍 Auto-tag feeds with source and country (inferred from URL or input)
* 🧠 Handles non-English characters using UTF-8 encoding
* 🛡️ Robust error handling and user-friendly interface

---

## 🛠 Technologies Used

* **Python 3.12+**
* [Streamlit](https://streamlit.io/) – UI framework
* [Feedparser](https://pythonhosted.org/feedparser/) – For parsing RSS feeds
* [Pandas](https://pandas.pydata.org/) – For data manipulation and storage

---

## 📁 File Structure

```
rss-news-scraper/
├── rss_news_scraper.py        # Main Streamlit App
├── requirements.txt           # Python dependencies
├── sample_output.csv          # Example output data (optional)
└── README.md                  # Project documentation
```

---

## 🚀 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/rss-news-scraper.git
cd rss-news-scraper
```

### 2. Install Dependencies

Create a virtual environment (optional but recommended):

```bash
python -m venv venv
```

Activate the virtual environment:

* **Windows**:

  ```bash
  venv\Scripts\activate
  ```
* **macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

Then install the required packages:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install streamlit feedparser pandas
```

### 3. Run the Streamlit App

```bash
streamlit run rss_news_scraper.py
```

---

## 📋 How to Use the App

1. Launch the app in your browser.
2. Paste a valid RSS feed URL into the input box.
3. Click **Scrape Feed**.
4. View the results in a live table.
5. Use **Download as CSV** or **Download as JSON** to save the data.

---

## 🧪 Example RSS Feed URLs

* **BBC News (UK):** [http://feeds.bbci.co.uk/news/rss.xml](http://feeds.bbci.co.uk/news/rss.xml)
* **CNN (US):** [http://rss.cnn.com/rss/edition.rss](http://rss.cnn.com/rss/edition.rss)
* **Al Jazeera (Middle East):** [https://www.aljazeera.com/xml/rss/all.xml](https://www.aljazeera.com/xml/rss/all.xml)
* **NHK (Japan):** [https://www3.nhk.or.jp/rss/news/cat0.xml](https://www3.nhk.or.jp/rss/news/cat0.xml)

✅ You can test with feeds from 20+ countries by finding their RSS links.

---

## 📦 Output Format (per article)

| Field     | Description                         |
| --------- | ----------------------------------- |
| Title     | News headline                       |
| Published | Publication date                    |
| Summary   | Article snippet or description      |
| Link      | URL to the full article             |
| Source    | Name of the news agency             |
| Country   | Country name (inferred or provided) |

---

## 🧠 Bonus Features to Try (Optional)

* 🔁 Auto-refresh feeds using `streamlit_autorefresh` or cron jobs
* 🌐 Detect language using `langdetect`
* 🗃️ Store results in SQLite/PostgreSQL
* ⚙️ Create an API using Flask or Django to serve data externally
* 📅 Backdate historical data using third-party news APIs

---

## 📦 Requirements

Add this to your `requirements.txt`:

```
streamlit
feedparser
pandas
```

---

## 📸 Screenshots 


---

## 👨‍💻 Author

**Your Name**
🔗 GitHub: [https://github.com/yourusername](https://github.com/Vinodk-17)
🔗 LinkedIn: [https://linkedin.com/in/yourprofile](https://www.linkedin.com/in/vinod-kuril-6398b5220/)

---

