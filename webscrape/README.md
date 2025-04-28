# LinkedIn Job/Internship Web Scraper

This project is a simple **web application** that allows users to search for **Jobs** or **Internships** on LinkedIn, based on custom input parameters like **keywords**, **location**, **time posted**, and **job type**.

## How It Works

1. **User fills out the search form** (job keyword, location, etc.) and clicks **Search**.
2. **Flask backend** triggers the **scraper** (`scraper.py`), which uses **Selenium** to open LinkedIn and collect job postings.
3. The scraped jobs are **saved into a JSON file**.
4. Flask **reads the JSON data** and passes it to the frontend.
5. **Jobs are displayed** dynamically using a template.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/linkedin-job-scraper.git
cd linkedin-job-scraper
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate.bat    # Windows
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
python app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

---

## Important Notes

- **Chrome browser** must be installed, since Selenium uses **ChromeDriver**.
- **LinkedIn scraping** is done without login. Only public job listings are scraped.
- Excessive scraping might trigger LinkedIn anti-bot protections. (Use responsibly!)
- Make sure you have **Google ChromeDriver** version matching your Chrome installed. (`webdriver-manager` usually handles it automatically.)

---

## Folder Structure
```
linkedin_ws.py         #Separate scraper logic (Main)
test_website/
│
├── app.py             # Flask server
├── scraper.py         # Selenium scraper logic
├── templates/
│   ├── index.html     # Main search page
├── requirements.txt   # Python dependencies
└── README.md          # Project description
```