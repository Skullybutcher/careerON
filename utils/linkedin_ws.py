#!/usr/bin/env python3
"""
LinkedIn Job & Internship Scraper (API-based)

This script uses LinkedIn's Guest API endpoint to fetch job listings directly,
replacing the previous Selenium-based approach with lightweight HTTP calls.
"""
import json
from datetime import datetime

import requests
import time
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def scrape_jobs_stream(
    keywords: str,
    location: str,
    time_filter: str,
    job_type: str,
    max_results: int = 25,
    page_size: int = 25,
    work_type: str = '',
    experience: str = ''
):
    """
    Generator: fetch jobs page-by-page and yield each job immediately.
    """
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        'keywords': keywords,
        'location': location,
        'start': 0,
        'count': page_size,
    }

    # map filters (same as before)...
    tf_map = {'24h':'r86400','week':'r604800','month':'r2592000'}
    if time_filter in tf_map:
        params['f_TPR'] = tf_map[time_filter]

    jt_map = {
        'full-time':'F','part-time':'P','contract':'C',
        'temporary':'T','volunteer':'V','internship':'I'
    }
    if job_type.lower() in jt_map:
        params['f_JT'] = jt_map[job_type.lower()]

    if work_type in {'1','2','3'}:
        params['f_WT'] = work_type
    if experience in {'1','2','3','4','5','6'}:
        params['f_EX'] = experience

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/112.0.0.0 Safari/537.36'
        )
    }

    count = 0
    while count < max_results:
        try:
            resp = requests.get(base_url, params=params, headers=headers, timeout=5)
        except requests.RequestException as e:
            logger.warning(f"[API] Request failed: {e}")
            break

        if resp.status_code != 200 or not resp.text.strip():
            logger.warning(f"[API] Bad response ({resp.status_code}) or empty.")
            break

        text = resp.text.strip()
        # Try JSON first
        batch = []
        if text.startswith('{'):
            try:
                data = resp.json()
                for job in data.get('elements', []):
                    batch.append({
                        'title':    job.get('title'),
                        'company':  job.get('companyName'),
                        'location': job.get('formattedLocation'),
                        'posted':   job.get('listedAt'),
                        'link':     "https://linkedin.com" + job.get('jobPostingUrl','')
                    })
            except ValueError:
                logger.info("[API] JSON parse failed, fallback to HTML")

        if not batch:
            # HTML fallback
            soup = BeautifulSoup(text, 'html.parser')
            for li in soup.select('li'):
                h3 = li.select_one('h3')
                h4 = li.select_one('h4')
                a  = li.select_one('a')
                if not (h3 and h4 and a):
                    continue
                # print(h3, h4, a)
                loc = li.select_one('.job-search-card__location')
                t   = li.select_one('time')
                href = a.get('href')
                if href and not href.startswith('http'):
                    href = "https://linkedin.com" + href
                batch.append({
                    'title':    h3.get_text(strip=True),
                    'company':  h4.get_text(strip=True),
                    'location': loc.get_text(strip=True) if loc else None,
                    'posted':   (t.get('datetime') if t and t.has_attr('datetime') else (t.get_text(strip=True) if t else None)),
                    'link':     href
                })

        if not batch:
            break

        for job in batch:
            if count >= max_results:
                return
            yield job
            count += 1

        params['start'] += page_size
        time.sleep(0.1)


def get_user_input():
    """
    Prompt the user for search criteria.
    Returns:
        tuple: (keywords, location, time_filter, job_type, max_results)
    """
    keywords = input("Enter job keywords (e.g. Python Engineer or Data Science Internship): ").strip()
    location = input("Enter location (city, region, country): ").strip()
    time_filter = input("Enter time filter ('24h', 'week', 'month' or 'any'): ").strip().lower() or 'any'
    job_type = input(
        "Enter job type ('full-time', 'part-time', 'contract', 'temporary', 'volunteer', 'internship' or blank): "
    ).strip().lower()
    max_results_input = input("Enter max results [default: 25]: ").strip()
    max_results = int(max_results_input) if max_results_input.isdigit() else 25
    return keywords, location, time_filter, job_type, max_results

def scrape_linkedin_jobs(keywords, location, time_filter='any', job_type='', max_results=25):
    """
    Fetch job listings via the scraper_api.stream generator.
    Args:
        keywords (str): Search keywords.
        location (str): Job location.
        time_filter (str): '24h', 'week', 'month', or 'any'.
        job_type (str): Type of job.
        max_results (int): Maximum number of jobs to fetch.
    Returns:
        list: A list of job dictionaries with keys: title, company, location, date_posted, link.
    """
    listings = []
    for job in scrape_jobs_stream(
        keywords=keywords,
        location=location,
        time_filter=time_filter,
        job_type=job_type,
        max_results=max_results
    ):
        listings.append({
            'title': job.get('title'),
            'company': job.get('company'),
            'location': job.get('location'),
            'date_posted': job.get('posted'),
            'link': job.get('link')
        })
    return listings

def main():
    keywords, location, time_filter, job_type, max_results = get_user_input()
    if not keywords or not location:
        print("Error: 'keywords' and 'location' are required.")
        return

    listings = scrape_linkedin_jobs(
        keywords, location, time_filter, job_type, max_results
    )

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"linkedin_jobs_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)

    print(f"Scraped {len(listings)} listings. Saved to {filename}")

if __name__ == '__main__':
    main()
