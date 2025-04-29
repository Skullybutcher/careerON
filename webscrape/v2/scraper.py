# # scraper.py
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time

# def scrape_jobs_generator(keywords, location, time_filter, job_type, max_results=60):
#     """
#     Generator that yields up to max_results job dicts.
#     """
#     # ─── Build URL ───────────────────────────────────────────────
#     base = (
#         "https://www.linkedin.com/jobs/search/"
#         f"?keywords={keywords.replace(' ', '%20')}"
#         f"&location={location.replace(' ', '%20')}"
#     )
#     tf_map = {'24h':'1','week':'2','month':'3'}
#     if time_filter in tf_map:
#         base += f"&f_TP={tf_map[time_filter]}"
#     if job_type:
#         base += f"&f_JT={job_type.lower()}"

#     # ─── Chrome & headless opts ──────────────────────────────────
#     opts = Options()
#     opts.page_load_strategy = 'eager'
#     opts.add_argument("--headless")
#     opts.add_experimental_option("prefs", {
#         "profile.managed_default_content_settings.images": 2,
#     })

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()), options=opts
#     )
#     wait = WebDriverWait(driver, 5)

#     seen = set()
#     count = 0
#     page_size = 25

#     for start in range(0, page_size * 4, page_size):
#         if count >= max_results:
#             break

#         driver.get(f"{base}&start={start}")
#         try:
#             wait.until(EC.presence_of_element_located((
#                 By.CSS_SELECTOR, "ul.jobs-search__results-list li"
#             )))
#         except:
#             break

#         cards = driver.find_elements(
#             By.CSS_SELECTOR, "ul.jobs-search__results-list li"
#         )
#         for card in cards:
#             if count >= max_results:
#                 break
#             try:
#                 h3 = card.find_element(By.TAG_NAME, "h3")
#                 h4 = card.find_element(By.TAG_NAME, "h4")
#                 a  = card.find_element(By.TAG_NAME, "a")

#                 title   = h3.text.strip()
#                 company = h4.text.strip()
#                 href    = a.get_attribute("href")

#                 if not title or not company or href in seen:
#                     continue
#                 seen.add(href)

#                 loc = card.find_element(
#                     By.CSS_SELECTOR, "span.job-search-card__location"
#                 ).text.strip()
#                 t = card.find_element(By.TAG_NAME, "time")
#                 posted = t.get_attribute("datetime") or t.text.strip()

#                 job = {
#                     "title":    title,
#                     "company":  company,
#                     "location": loc,
#                     "posted":   posted,
#                     "link":     href
#                 }
#                 count += 1
#                 yield job

#             except:
#                 continue

#     driver.quit()
# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_jobs_generator(keywords, location, time_filter, job_type, max_results=60):
    """
    Scrape up to max_results LinkedIn jobs, honoring time and job-type filters.
    """
    # ─── Build the base URL ───────────────────────────────────────────
    base = (
      "https://www.linkedin.com/jobs/search/"
      f"?keywords={keywords.replace(' ', '%20')}"
      f"&location={location.replace(' ', '%20')}"
    )

    # time‐posted filter codes (1=24h,2=week,3=month)
    tf_map = {'24h':'1','week':'2','month':'3'}
    if time_filter in tf_map:
        base += f"&f_TP={tf_map[time_filter]}"

    # job‐type filter codes
    jt_map = {
        'full-time':'F','part-time':'P','contract':'C',
        'temporary':'T','volunteer':'V','internship':'I'
    }
    jt_key = job_type.strip().lower()
    if jt_key in jt_map:
        base += f"&f_JT={jt_map[jt_key]}"

    print("Base URL:", base)

    # ─── Chrome setup ────────────────────────────────────────────────
    opts = Options()
    opts.page_load_strategy = 'eager'
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    prefs = {
      "profile.managed_default_content_settings.images": 2,
      "profile.managed_default_content_settings.stylesheets": 2,
      "profile.managed_default_content_settings.fonts": 2
    }
    opts.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(
      service=Service(ChromeDriverManager().install()),
      options=opts
    )
    wait = WebDriverWait(driver, 5)

    jobs = []
    seen = set()
    page_size = 25

    # ─── Loop pages until we have enough ────────────────────────────
    for start in range(0, page_size * 6, page_size):  # try up to 6 pages (~150 jobs)
        if len(jobs) >= max_results:
            break

        url = f"{base}&start={start}"
        print(f"→ Loading start={start}")
        driver.get(url)

        # wait for the list container
        try:
            list_sel = "ul.jobs-search__results-list, ul.jobs-search-results__list"
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, list_sel)))
        except:
            print("  • No jobs list found, breaking.")
            break

        # scroll its container to force-load all cards
        container = driver.find_element(By.CSS_SELECTOR, list_sel)
        last_h = driver.execute_script("return arguments[0].scrollHeight", container)
        while True:
            driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight);", container
            )
            time.sleep(0.5)
            new_h = driver.execute_script("return arguments[0].scrollHeight", container)
            if new_h == last_h:
                break
            last_h = new_h

        # grab every <li> now
        cards = container.find_elements(By.CSS_SELECTOR, "li")
        new_count = 0

        for card in cards:
            if len(jobs) >= max_results:
                break
            try:
                title_el = card.find_element(By.CSS_SELECTOR, "h3")
                comp_el  = card.find_element(By.CSS_SELECTOR, "h4")
                link_el  = card.find_element(By.CSS_SELECTOR,
                              "a.base-card__full-link, a.job-card-list__title")

                title   = title_el.text.strip()
                company = comp_el.text.strip()
                href    = link_el.get_attribute("href")

                if not title or not company or href in seen:
                    continue
                seen.add(href)

                loc = card.find_element(
                    By.CSS_SELECTOR, "span.job-search-card__location"
                ).text.strip()
                t = card.find_element(By.TAG_NAME, "time")
                posted = t.get_attribute("datetime") or t.text.strip()

                jobs.append({
                  "title":    title,
                  "company":  company,
                  "location": loc,
                  "posted":   posted,
                  "link":     href
                })
                new_count += 1

            except:
                continue

        print(f"  • Page {start//page_size}: +{new_count} new (total {len(jobs)})")
        if new_count == 0:
            break

    driver.quit()
    print(f"Scraped {len(jobs)} listings (requested {max_results}).")
    return jobs
