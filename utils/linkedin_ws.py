#!/usr/bin/env python3
"""
LinkedIn Job & Internship Scraper

This script uses Selenium to scrape LinkedIn job (or internship) listings based on user input:
- Keywords (e.g. "Python Engineer" or "Data Science Internship")
- Location (city, region, country)
- Time posted filter (last 24 hrs, last week, last month)
- Job type filter (Full-time, Part-time, Contract, Internship, etc.)

Outputs a JSON file with a list of job entries including:
- Title
- Company
- Location
- Date posted
- Job link

Requirements:
- Python 3.x
- selenium
- webdriver-manager
- beautifulsoup4

Usage:
$ pip install selenium webdriver-manager beautifulsoup4
$ python linkedin_job_scraper.py
"""

import json
import time
import urllib.parse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Map user-friendly filters to LinkedIn URL parameters
time_mapping = {
    '24h': '1',      # Past 24 hours
    'week': '2',     # Past week
    'month': '3',    # Past month
    'any': '4'       # Any time
}
job_type_mapping = {
    'full-time': 'F',
    'part-time': 'P',
    'contract': 'C',
    'temporary': 'T',
    'volunteer': 'V',
    'internship': 'I'
}

def get_user_input():
    keywords = input("Enter job keywords (e.g. Python Engineer or Data Science Internship): ").strip()
    location = input("Enter job location (city, region, country): ").strip()
    print("Time filters: 24h, week, month, any")
    time_filter = input("Choose time filter [24h/week/month/any]: ").strip().lower()
    print("Job types: full-time, part-time, contract, temporary, volunteer, internship")
    job_type = input("Choose job type (or leave blank for all): ").strip().lower()

    tf = time_mapping.get(time_filter, '1')
    jt = job_type_mapping.get(job_type, '')
    return keywords, location, tf, jt


def build_linkedin_url(keywords, location, time_param, job_type_param):
    base = "https://www.linkedin.com/jobs/search/"
    params = {
        'keywords': keywords,
        'location': location,
        'f_TP': time_param,
    }
    if job_type_param:
        params['f_JT'] = job_type_param
    query = urllib.parse.urlencode(params)
    return f"{base}?{query}"


def scrape_listings(driver):
    # Accept cookies banner if present
    try:
        accept_btn = driver.find_element(By.XPATH, "//button[contains(., 'Accept') and contains(., 'cookies')]")
        accept_btn.click()
        time.sleep(1)
    except Exception:
        pass

    # Scroll through the results container to load all jobs
    try:
        container = driver.find_element(By.CSS_SELECTOR, 'ul.jobs-search__results-list')
        last_height = driver.execute_script("return arguments[0].scrollHeight", container)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", container)
            if new_height == last_height:
                break
            last_height = new_height
    except Exception:
        # Fallback to scrolling the window
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    # Parse listings
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    cards = soup.select('ul.jobs-search__results-list li')
    listings = []
    for card in cards:
        title_elem = card.select_one('h3.base-search-card__title')
        title = title_elem.get_text(strip=True) if title_elem else None
        company_elem = card.select_one('h4.base-search-card__subtitle')
        company = company_elem.get_text(strip=True) if company_elem else None
        loc_elem = card.select_one('span.job-search-card__location')
        location_text = loc_elem.get_text(strip=True) if loc_elem else None
        date_elem = card.select_one('time')
        date_posted = date_elem['datetime'] if date_elem and date_elem.has_attr('datetime') else None
        link_elem = card.select_one('a.base-card__full-link')
        link = link_elem['href'] if link_elem else None
        if title and link:
            listings.append({
                'title': title,
                'company': company,
                'location': location_text,
                'date_posted': date_posted,
                'link': link
            })
    return listings

def scrape_linkedin_jobs(keywords, location, time_filter='any', job_type=''):
    """
    Scrape LinkedIn jobs for given keywords and location.
    """
    from selenium.webdriver.chrome.options import Options

    tf = time_mapping.get(time_filter, '4')  # default to 'any'
    jt = job_type_mapping.get(job_type, '')
    search_url = build_linkedin_url(keywords, location, tf, jt)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(search_url)

    listings = scrape_listings(driver)
    driver.quit()

    return listings

def main():
    keywords, location, time_param, job_type_param = get_user_input()
    search_url = build_linkedin_url(keywords, location, time_param, job_type_param)
    print(f"Navigating to: {search_url}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(search_url)

    listings = scrape_listings(driver)
    driver.quit()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"linkedin_jobs_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print(f"Scraped {len(listings)} listings. Saved to {filename}")

if __name__ == '__main__':
    main()
