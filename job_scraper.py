import requests
from bs4 import BeautifulSoup
from telegram import Bot
import json
import os
from datetime import datetime
import time

# ------------------------ Telegram Settings ------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

# ------------------------ Job Tracking ------------------------
SENT_FILE = "sent_jobs.json"

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r") as f:
        sent_jobs = set(json.load(f))
else:
    sent_jobs = set()

# ------------------------ Profile Keywords ------------------------
KEYWORDS = [
    "AI", "ML", "Machine Learning", "Computer Vision",
    "Autonomous Driving", "Generative AI", "GenAI", "Gen AI", "LLM"
]

# ------------------------ Helper Functions ------------------------
def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def job_matches_keywords(title, description=""):
    combined_text = f"{title} {description}".lower()
    return any(keyword.lower() in combined_text for keyword in KEYWORDS)

def safe_request(url, site_name, failed_sites):
    """Make a GET request safely with timeout and error handling."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        time.sleep(2)  # small delay to avoid being blocked
        return response.text
    except Exception as e:
        print(f"Request failed for {site_name} ({url}): {e}")
        failed_sites.append(site_name)
        return None

# ------------------------ Individual Site Scrapers ------------------------
def scrape_datacareer(failed_sites):
    jobs = []
    url = "https://www.datacareer.de/jobs/?categories%5B%5D=Artificial+Intelligence"
    html = safe_request(url, "Datacareer", failed_sites)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for job_card in soup.find_all("div", class_="job-listing"):
            try:
                title = job_card.find("h2").text.strip()
                company = job_card.find("div", class_="company").text.strip()
                link = job_card.find("a")["href"]
                job_type = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
                job_id = link
                if job_id not in sent_jobs and job_matches_keywords(title):
                    if "full-time" in job_type.lower() or "internship" in job_type.lower():
                        jobs.append(f"{title} at {company} | {link} | {job_type}")
                        sent_jobs.add(job_id)
            except Exception as e:
                print(f"Datacareer job parse error: {e}")
    return jobs

def scrape_stepstone(failed_sites):
    jobs = []
    url = "https://www.stepstone.de/jobs/ai"
    html = safe_request(url, "StepStone", failed_sites)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for job_card in soup.find_all("div", class_="job-listing"):
            try:
                title = job_card.find("h2").text.strip()
                company = job_card.find("div", class_="company").text.strip()
                link = job_card.find("a")["href"]
                job_type = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
                job_id = link
                if job_id not in sent_jobs and job_matches_keywords(title):
                    if "full-time" in job_type.lower() or "internship" in job_type.lower():
                        jobs.append(f"{title} at {company} | {link} | {job_type}")
                        sent_jobs.add(job_id)
            except Exception as e:
                print(f"StepStone job parse error: {e}")
    return jobs

def scrape_indeed(failed_sites):
    jobs = []
    url = "https://www.indeed.de/jobs?q=AI&l=Germany"
    html = safe_request(url, "Indeed", failed_sites)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for job_card in soup.find_all("div", class_="job_seen_beacon"):
            try:
                title = job_card.find("h2").text.strip()
                company = job_card.find("span", class_="companyName").text.strip()
                link = "https://www.indeed.de" + job_card.find("a")["href"]
                job_type = job_card.find("div", class_="job-snippet").text.strip() if job_card.find("div", class_="job-snippet") else ""
                job_id = link
                if job_id not in sent_jobs and job_matches_keywords(title):
                    if "full-time" in job_type.lower() or "internship" in job_type.lower():
                        jobs.append(f"{title} at {company} | {link} | {job_type}")
                        sent_jobs.add(job_id)
            except Exception as e:
                print(f"Indeed job parse error: {e}")
    return jobs

def scrape_glassdoor(failed_sites):
    jobs = []
    url = "https://www.glassdoor.de/Job/germany-ai-jobs-SRCH_IL.0,7_IN96_KO8,10.htm"
    html = safe_request(url, "Glassdoor", failed_sites)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for job_card in soup.find_all("li", class_="jl"):
            try:
                title = job_card.find("a", class_="jobLink").text.strip()
                company = job_card.find("div", class_="jobEmpolyerName").text.strip()
                link = "https://www.glassdoor.de" + job_card.find("a", class_="jobLink")["href"]
                job_type = job_card.find("div", class_="jobLabels").text.strip() if job_card.find("div", class_="jobLabels") else ""
                job_id = link
                if job_id not in sent_jobs and job_matches_keywords(title):
                    if "full-time" in job_type.lower() or "internship" in job_type.lower():
                        jobs.append(f"{title} at {company} | {link} | {job_type}")
                        sent_jobs.add(job_id)
            except Exception as e:
                print(f"Glassdoor job parse error: {e}")
    return jobs

def scrape_stackoverflow(failed_sites):
    jobs = []
    url = "https://stackoverflow.com/jobs?tl=artificial-intelligence"
    html = safe_request(url, "StackOverflow", failed_sites)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for job_card in soup.find_all("div", class_="-job"):
            try:
                title = job_card.find("a", class_="s-link").text.strip()
                company = job_card.find("h3", class_="fc-black-700").text.strip()
                link = "https://stackoverflow.com" + job_card.find("a", class_="s-link")["href"]
                job_type = job_card.find("span", class_="fc-black-500").text.strip() if job_card.find("span", class_="fc-black-500") else ""
                job_id = link
                if job_id not in sent_jobs and job_matches_keywords(title):
                    if "full-time" in job_type.lower() or "internship" in job_type.lower():
                        jobs.append(f"{title} at {company} | {link} | {job_type}")
                        sent_jobs.add(job_id)
            except Exception as e:
                print(f"StackOverflow job parse error: {e}")
    return jobs

# ------------------------ Combine all sites ------------------------
def scrape_all_sites():
    all_jobs = []
    failed_sites = []
    all_jobs.extend(scrape_datacareer(failed_sites))
    all_jobs.extend(scrape_stepstone(failed_sites))
    all_jobs.extend(scrape_indeed(failed_sites))
    all_jobs.extend(scrape_glassdoor(failed_sites))
    all_jobs.extend(scrape_stackoverflow(failed_sites))
    return all_jobs, failed_sites

# ------------------------ Main Function ------------------------
def main():
    now = datetime.now()
    if 8 <= now.hour <= 18:  # only between 8 AM - 6 PM
        new_jobs, failed_sites = scrape_all_sites()
        messages = []
        if new_jobs:
            messages.append("🧑‍💻 Latest AI/ML Jobs in Germany:\n\n" + "\n".join(new_jobs[:10]))
        if failed_sites:
            messages.append("⚠️ Could not scrape the following sites:\n" + "\n".join(failed_sites))
        if messages:
            send_telegram_message("\n\n".join(messages))
            # Save sent jobs
            with open(SENT_FILE, "w") as f:
                json.dump(list(sent_jobs), f)

if __name__ == "__main__":
    main()
