import requests
from bs4 import BeautifulSoup
from telegram import Bot
import json
import os
from datetime import datetime

import os
from telegram import Bot

# Get token and chat ID from GitHub Actions environment
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

# ------------------------ Individual Site Scrapers ------------------------
def scrape_datacareer():
    jobs = []
    url = "https://www.datacareer.de/jobs/?categories%5B%5D=Artificial+Intelligence"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="job-listing"):
        title = job_card.find("h2").text.strip()
        company = job_card.find("div", class_="company").text.strip()
        link = job_card.find("a")["href"]
        job_type = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            if "full-time" in job_type.lower() or "internship" in job_type.lower():
                jobs.append(f"{title} at {company} | {link} | {job_type}")
                sent_jobs.add(job_id)
    return jobs

def scrape_stepstone():
    jobs = []
    url = "https://www.stepstone.de/jobs/ai"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="job-listing"):
        title = job_card.find("h2").text.strip()
        company = job_card.find("div", class_="company").text.strip()
        link = job_card.find("a")["href"]
        job_type = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            if "full-time" in job_type.lower() or "internship" in job_type.lower():
                jobs.append(f"{title} at {company} | {link} | {job_type}")
                sent_jobs.add(job_id)
    return jobs

def scrape_indeed():
    jobs = []
    url = "https://www.indeed.de/jobs?q=AI&l=Germany"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="job_seen_beacon"):
        title = job_card.find("h2").text.strip()
        company = job_card.find("span", class_="companyName").text.strip()
        link = "https://www.indeed.de" + job_card.find("a")["href"]
        job_type = job_card.find("div", class_="job-snippet").text.strip() if job_card.find("div", class_="job-snippet") else ""
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            if "full-time" in job_type.lower() or "internship" in job_type.lower():
                jobs.append(f"{title} at {company} | {link} | {job_type}")
                sent_jobs.add(job_id)
    return jobs

def scrape_glassdoor():
    jobs = []
    url = "https://www.glassdoor.de/Job/germany-ai-jobs-SRCH_IL.0,7_IN96_KO8,10.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("li", class_="jl"):
        title = job_card.find("a", class_="jobLink").text.strip()
        company = job_card.find("div", class_="jobEmpolyerName").text.strip()
        link = "https://www.glassdoor.de" + job_card.find("a", class_="jobLink")["href"]
        job_type = job_card.find("div", class_="jobLabels").text.strip() if job_card.find("div", class_="jobLabels") else ""
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            if "full-time" in job_type.lower() or "internship" in job_type.lower():
                jobs.append(f"{title} at {company} | {link} | {job_type}")
                sent_jobs.add(job_id)
    return jobs

def scrape_stackoverflow():
    jobs = []
    url = "https://stackoverflow.com/jobs?tl=artificial-intelligence"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    for job_card in soup.find_all("div", class_="-job"):
        title = job_card.find("a", class_="s-link").text.strip()
        company = job_card.find("h3", class_="fc-black-700").text.strip()
        link = "https://stackoverflow.com" + job_card.find("a", class_="s-link")["href"]
        job_type = job_card.find("span", class_="fc-black-500").text.strip() if job_card.find("span", class_="fc-black-500") else ""
        job_id = link
        if job_id not in sent_jobs and job_matches_keywords(title):
            if "full-time" in job_type.lower() or "internship" in job_type.lower():
                jobs.append(f"{title} at {company} | {link} | {job_type}")
                sent_jobs.add(job_id)
    return jobs

# ------------------------ Combine all sites ------------------------
def scrape_all_sites():
    all_jobs = []
    all_jobs.extend(scrape_datacareer())
    all_jobs.extend(scrape_stepstone())
    all_jobs.extend(scrape_indeed())
    all_jobs.extend(scrape_glassdoor())
    all_jobs.extend(scrape_stackoverflow())
    return all_jobs

# ------------------------ Main Function ------------------------
def main():
    now = datetime.now()
    if 8 <= now.hour <= 18:  # only between 8 AM - 6 PM
        new_jobs = scrape_all_sites()
        if new_jobs:
            message = "🧑‍💻 Latest AI/ML Jobs in Germany:\n\n" + "\n".join(new_jobs[:10])
            send_telegram_message(message)
            # Save sent jobs
            with open(SENT_FILE, "w") as f:
                json.dump(list(sent_jobs), f)

# ------------------------ Run Script ------------------------
if __name__ == "__main__":
    main()

