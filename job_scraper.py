import os
import json
import asyncio
import requests
from bs4 import BeautifulSoup
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

# ------------------------ Helper Functions ------------------------
def job_matches_keywords(title, description=""):
    combined_text = f"{title} {description}".lower()
    return any(keyword.lower() in combined_text for keyword in KEYWORDS)

# ------------------------ Scrapers ------------------------
def scrape_datacareer():
    jobs = []
    try:
        url = "https://www.datacareer.de/jobs/?categories%5B%5D=Artificial+Intelligence"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="job-listing"):
            title = job_card.find("h2").text.strip()
            company = job_card.find("div", class_="company").text.strip()
            link = job_card.find("a")["href"]
            description = job_card.get_text(separator=" ").strip()
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
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="job-listing"):
            title = job_card.find("h2").text.strip()
            company = job_card.find("div", class_="company").text.strip()
            link = job_card.find("a")["href"]
            description = job_card.get_text(separator=" ").strip()
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
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for job_card in soup.find_all("div", class_="job_seen_beacon"):
            title = job_card.find("h2").text.strip()
            company = job_card.find("span", class_="companyName").text.strip()
            link = "https://www.indeed.de" + job_card.find("a")["href"]
            description = job_card.get_text(separator=" ").strip()
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title, description):
                jobs.append(f"{title} at {company} | {link}")
                sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape Indeed: {e}"))
    return jobs

def scrape_all_sites():
    all_jobs = []
    all_jobs.extend(scrape_datacareer())
    all_jobs.extend(scrape_stepstone())
    all_jobs.extend(scrape_indeed())
    # Add more scrapers if needed
    return all_jobs

# ------------------------ Main ------------------------
async def main():
    now = datetime.now()
    if 8 <= now.hour <= 18:  # Only run between 8 AM - 6 PM
        new_jobs = scrape_all_sites()

        # Save sent jobs
        with open(SENT_FILE, "w") as f:
            json.dump(list(sent_jobs), f)

        # Prepare message
        if new_jobs:
            message = "🧑‍💻 New AI/ML Jobs:\n\n" + "\n".join(new_jobs[:10])
        else:
            message = "ℹ️ No new AI/ML jobs found at this time."

        # Include all jobs in sent_jobs.json
        if sent_jobs:
            message += "\n\n📦 Last 10 jobs in sent_jobs.json:\n" + "\n".join(list(sent_jobs)[-10:])

        await send_telegram_message(message)

if __name__ == "__main__":
    asyncio.run(main())
