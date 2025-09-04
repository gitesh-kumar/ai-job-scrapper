import requests
from bs4 import BeautifulSoup
import json
import os
import asyncio
from telegram import Bot
from datetime import datetime

# ------------------------ Telegram Setup ------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

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

def job_matches_keywords(title, description=""):
    combined_text = f"{title} {description}".lower()
    return any(keyword.lower() in combined_text for keyword in KEYWORDS)

# ------------------------ Individual Site Scrapers ------------------------
def scrape_datacareer():
    jobs = []
    try:
        url = "https://www.datacareer.de/jobs/?categories%5B%5D=Artificial+Intelligence"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="job-listing"):
            title = job_card.find("h2").text.strip()
            company = job_card.find("div", class_="company").text.strip()
            link = job_card.find("a")["href"]
            description = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title, description):
                jobs.append(f"{title} at {company} | {link}")
                sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape DataCareer: {e}"))
    return jobs

def scrape_stepstone():
    jobs = []
    try:
        url = "https://www.stepstone.de/jobs/ai"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="job-listing"):
            title = job_card.find("h2").text.strip()
            company = job_card.find("div", class_="company").text.strip()
            link = job_card.find("a")["href"]
            description = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title, description):
                jobs.append(f"{title} at {company} | {link}")
                sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape StepStone: {e}"))
    return jobs

def scrape_indeed():
    jobs = []
    try:
        url = "https://www.indeed.de/jobs?q=AI&l=Germany"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="job_seen_beacon"):
            title = job_card.find("h2").text.strip()
            company = job_card.find("span", class_="companyName").text.strip()
            link = "https://www.indeed.de" + job_card.find("a")["href"]
            description = job_card.find("div", class_="job-snippet").text.strip() if job_card.find("div", class_="job-snippet") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title, description):
                jobs.append(f"{title} at {company} | {link}")
                sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape Indeed: {e}"))
    return jobs

def scrape_glassdoor():
    jobs = []
    try:
        url = "https://www.glassdoor.de/Job/germany-ai-jobs-SRCH_IL.0,7_IN96_KO8,10.htm"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("li", class_="jl"):
            title = job_card.find("a", class_="jobLink").text.strip()
            company = job_card.find("div", class_="jobEmpolyerName").text.strip()
            link = "https://www.glassdoor.de" + job_card.find("a", class_="jobLink")["href"]
            description = job_card.find("div", class_="jobLabels").text.strip() if job_card.find("div", class_="jobLabels") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title, description):
                jobs.append(f"{title} at {company} | {link}")
                sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape Glassdoor: {e}"))
    return jobs

def scrape_stackoverflow():
    jobs = []
    try:
        url = "https://stackoverflow.com/jobs?tl=artificial-intelligence"
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="-job"):
            title = job_card.find("a", class_="s-link").text.strip()
            company = job_card.find("h3", class_="fc-black-700").text.strip()
            link = "https://stackoverflow.com" + job_card.find("a", class_="s-link")["href"]
            description = job_card.find("span", class_="fc-black-500").text.strip() if job_card.find("span", class_="fc-black-500") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title, description):
                jobs.append(f"{title} at {company} | {link}")
                sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape StackOverflow: {e}"))
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
async def main():
    now = datetime.now()
    if 8 <= now.hour <= 18:  # only between 8 AM - 6 PM
        new_jobs = scrape_all_sites()
        if new_jobs:
            message = "🧑‍💻 Latest AI/ML Jobs in Germany:\n\n" + "\n".join(new_jobs[:20])
            await send_telegram_message(message)

        # Also send current sent jobs
        if sent_jobs:
            current_jobs_message = "💾 Current sent jobs:\n" + "\n".join(list(sent_jobs)[:20])
            await send_telegram_message(current_jobs_message)

        # Save sent jobs
        with open(SENT_FILE, "w") as f:
            json.dump(list(sent_jobs), f)

# ------------------------ Run Script ------------------------
if __name__ == "__main__":
    asyncio.run(main())
