# scraper_api.py

import requests
import time
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def scrape_jobs_via_api(
    keywords: str,
    location: str,
    time_filter: str,
    job_type: str,
    max_results: int = 60,
    page_size: int = 25,
    work_type: str = '',
    experience: str = ''
):
    """
    Fetch up to max_results job postings directly from LinkedIn's guest API endpoint.
    Handles both JSON and HTML fragment responses.
    
    Args:
        keywords: Job search keywords
        location: Job location
        time_filter: Time filter ('24h', 'week', 'month')
        job_type: Job type ('full-time', 'part-time', 'contract', etc.)
        max_results: Maximum number of results to return
        page_size: Number of results per page
        work_type: Work arrangement filter ('1', '2', '3')
        experience: Experience level filter ('1', '2', '3', '4', '5', '6')
    
    Returns:
        List of job dictionaries
    """
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    params = {
        'keywords': keywords,
        'location': location,
        'start': 0,
        'count': page_size,
    }

    # Map time filters
    tf_map = {'24h': 'r86400', 'week': 'r604800', 'month': 'r2592000'}
    if time_filter in tf_map:
        params['f_TPR'] = tf_map[time_filter]

    # Map job types
    jt_map = {
        'full-time': 'F', 'part-time': 'P', 'contract': 'C',
        'temporary': 'T', 'volunteer': 'V', 'internship': 'I'
    }
    jt = job_type.strip().lower()
    if jt in jt_map:
        params['f_JT'] = jt_map[jt]

    # Work arrangement filter
    if work_type in {'1', '2', '3'}:
        params['f_WT'] = work_type

    # Experience level filter
    if experience in {'1', '2', '3', '4', '5', '6'}:
        params['f_EX'] = experience

    headers = {
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/112.0.0.0 Safari/537.36'
        )
    }

    results = []
    while len(results) < max_results:
        try:
            resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        except requests.RequestException as e:
            logger.warning(f"[API] Request failed: {e}")
            break

        if resp.status_code != 200:
            logger.warning(f"[API] Non-200 status {resp.status_code}")
            break

        text = resp.text.strip()
        if not text:
            logger.warning("[API] Empty response, stopping.")
            break

        # First, try JSON
        jobs_batch = []
        if text.startswith('{'):
            try:
                data = resp.json()
                elements = data.get('elements') or []
                for job in elements:
                    jobs_batch.append({
                        'title': job.get('title'),
                        'company': job.get('companyName'),
                        'location': job.get('formattedLocation'),
                        'posted': job.get('listedAt'),
                        'link': "https://www.linkedin.com" + job.get('jobPostingUrl', '')
                    })
            except ValueError:
                logger.info("[API] JSON parse failed, falling back to HTML.")
        else:
            # Fallback: parse HTML fragment
            soup = BeautifulSoup(text, 'html.parser')
            for li in soup.select('li'):
                a = li.select_one('a')
                h3 = li.select_one('h3')
                h4 = li.select_one('h4')
                loc = li.select_one('.job-search-card__location')
                time_tag = li.select_one('time')

                if not (a and h3 and h4):
                    continue
                title = h3.get_text(strip=True)
                company = h4.get_text(strip=True)
                href = a.get('href')
                if href and not href.startswith('http'):
                    href = 'https://www.linkedin.com' + href

                jobs_batch.append({
                    'title': title,
                    'company': company,
                    'location': loc.get_text(strip=True) if loc else None,
                    'posted': time_tag.get('datetime') if time_tag and time_tag.has_attr('datetime') else (time_tag.get_text(strip=True) if time_tag else None),
                    'link': href
                })

        if not jobs_batch:
            logger.info("[API] No jobs parsed on this page, stopping.")
            break

        # Add up to max_results
        for job in jobs_batch:
            if len(results) >= max_results:
                break
            results.append(job)

        # Advance pagination
        params['start'] += page_size
        time.sleep(0.05)

    return results

