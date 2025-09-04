import os
import asyncio
import json
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
from time import sleep

# ------------------------ Telegram Setup ------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# ------------------------ Job Tracking ------------------------
SENT_FILE = "sent_jobs.json"

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_jobs = set(json.load(f))
else:
    sent_jobs = set()

# ------------------------ Keywords ------------------------
KEYWORDS = [
    "AI", "ML", "Machine Learning", "Computer Vision",
    "Autonomous Driving", "Generative AI", "GenAI", "Gen AI", "LLM"
]

# ------------------------ Helper Functions ------------------------
def job_matches_keywords(title, description=""):
    combined_text = f"{title} {description}".lower()
    return any(keyword.lower() in combined_text for keyword in KEYWORDS)

def safe_request(url, retries=2, timeout=30):
    """Try a request with retries."""
    for attempt in range(retries):
        try:
            return requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException:
            sleep(2)  # small delay before retry
    return None

# ------------------------ Site Scrapers ------------------------
def scrape_datacareer():
    jobs = []
    url = "https://www.datacareer.de/jobs/?categories%5B%5D=Artificial+Intelligence"
    response = safe_request(url)
    if not response:
        raise Exception("Could not reach DataCareer")
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="job-listing"):
        title = job_card.find("h2").text.strip()
        company = job_card.find("div", class_="company").text.strip()
        link = job_card.find("a")["href"]
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            jobs.append(f"{title} at {company} | {link}")
            sent_jobs.add(job_id)
    return jobs

def scrape_stepstone():
    jobs = []
    url = "https://www.stepstone.de/jobs/ai"
    response = safe_request(url)
    if not response:
        raise Exception("Could not reach StepStone")
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="job-listing"):
        title = job_card.find("h2").text.strip()
        company = job_card.find("div", class_="company").text.strip()
        link = job_card.find("a")["href"]
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            jobs.append(f"{title} at {company} | {link}")
            sent_jobs.add(job_id)
    return jobs

def scrape_indeed():
    jobs = []
    url = "https://www.indeed.de/jobs?q=AI&l=Germany"
    response = safe_request(url)
    if not response:
        raise Exception("Could not reach Indeed")
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="job_seen_beacon"):
        title = job_card.find("h2").text.strip()
        company = job_card.find("span", class_="companyName").text.strip()
        link = "https://www.indeed.de" + job_card.find("a")["href"]
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            jobs.append(f"{title} at {company} | {link}")
            sent_jobs.add(job_id)
    return jobs

def scrape_glassdoor():
    jobs = []
    url = "https://www.glassdoor.de/Job/germany-ai-jobs-SRCH_IL.0,7_IN96_KO8,10.htm"
    response = safe_request(url)
    if not response:
        raise Exception("Could not reach Glassdoor")
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("li", class_="jl"):
        title = job_card.find("a", class_="jobLink").text.strip()
        company_tag = job_card.find("div", class_="jobEmpolyerName")
        company = company_tag.text.strip() if company_tag else ""
        link = "https://www.glassdoor.de" + job_card.find("a", class_="jobLink")["href"]
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            jobs.append(f"{title} at {company} | {link}")
            sent_jobs.add(job_id)
    return jobs

def scrape_stackoverflow():
    jobs = []
    url = "https://stackoverflow.com/jobs?tl=artificial-intelligence"
    response = safe_request(url)
    if not response:
        raise Exception("Could not reach StackOverflow")
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="-job"):
        title_tag = job_card.find("a", class_="s-link")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        company_tag = job_card.find("h3", class_="fc-black-700")
        company = company_tag.text.strip() if company_tag else ""
        link = "https://stackoverflow.com" + title_tag["href"]
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            jobs.append(f"{title} at {company} | {link}")
            sent_jobs.add(job_id)
    return jobs

# ------------------------ Combine Sites ------------------------
def scrape_all_sites():
    all_jobs = []
    errors = []

    for scraper, name in [
        (scrape_datacareer, "DataCareer"),
        (scrape_stepstone, "StepStone"),
        (scrape_indeed, "Indeed"),
        (scrape_glassdoor, "Glassdoor"),
        (scrape_stackoverflow, "StackOverflow")
    ]:
        try:
            jobs = scraper()
            all_jobs.extend(jobs)
        except Exception as e:
            errors.append(f"⚠️ Could not scrape {name}: {str(e)}")

    return all_jobs, errors

# ------------------------ Main ------------------------
async def main():
    now = datetime.now()
    if 8 <= now.hour <= 18:  # Only between 8 AM - 6 PM
        all_jobs, errors = scrape_all_sites()

        # Compose final message
        messages = []
        if errors:
            messages.extend(errors)
        if all_jobs:
            messages.append("🧑‍💻 Latest AI/ML Jobs in Germany:\n" + "\n".join(all_jobs[:20]))
        messages.append(f"💾 Current sent jobs: {len(sent_jobs)}")

        # Send message
        await send_telegram_message("\n\n".join(messages))

        # Save sent jobs
        with open(SENT_FILE, "w") as f:
            json.dump(list(sent_jobs), f)

# ------------------------ Run ------------------------
if __name__ == "__main__":
    asyncio.run(main())
