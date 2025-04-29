# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_jobs(keywords, location, time_filter, job_type):
    # ─── Build the URL ─────────────────────────────────────────────
    base_url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={keywords.replace(' ', '%20')}"
        f"&location={location.replace(' ', '%20')}"
    )
    tf_map = {'24h':'1','week':'2','month':'3','any':'4'}
    if time_filter in tf_map:
        base_url += f"&f_TP={tf_map[time_filter]}"
    if job_type:
        base_url += f"&f_JT={job_type.lower()}"
    print("Navigating to:", base_url)

    # ─── Headless Chrome Setup ─────────────────────────────────────
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    driver.get(base_url)

    wait = WebDriverWait(driver, 10)
    # ─── Accept cookies if prompted ───────────────────────────────
    try:
        accept_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Accept cookies') or contains(text(),'Accept all')]")
        ))
        accept_btn.click()
    except Exception:
        pass

    # ─── Wait for the job-list container ─────────────────────────
    job_list_locator = (By.CSS_SELECTOR,
        "ul.jobs-search__results-list, ul.jobs-search-results__list"
    )
    wait.until(EC.presence_of_element_located(job_list_locator))

    # ─── Scroll that container until it stops growing ────────────
    scrollable = driver.find_element(*job_list_locator)
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)
    while True:
        driver.execute_script(
            "arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable
        )
        time.sleep(1)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)
        if new_height == last_height:
            break
        last_height = new_height

    # ─── Grab each job card from the rendered DOM ─────────────────
    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "ul.jobs-search__results-list li, ul.jobs-search-results__list li"
    )
    jobs = []
    for card in cards:
        try:
            title   = card.find_element(By.CSS_SELECTOR, "h3").text.strip()
            company = card.find_element(By.CSS_SELECTOR, "h4").text.strip()
            loc     = card.find_element(
                By.CSS_SELECTOR, "span.job-search-card__location"
            ).text.strip()
            # some times <time> has a datetime attr, other times just text
            try:
                posted = card.find_element(By.TAG_NAME, "time").get_attribute("datetime")
            except:
                posted = card.find_element(By.TAG_NAME, "time").text.strip()
            link = card.find_element(
                By.CSS_SELECTOR, "a.base-card__full-link, a.job-card-list__title"
            ).get_attribute("href")
        except Exception:
            # if any of the fields aren’t found, skip this card
            continue

        jobs.append({
            "title":   title,
            "company": company,
            "location": loc,
            "posted":   posted,
            "link":     link
        })

    driver.quit()
    print(f"Scraped {len(jobs)} listings.")
    return jobs
