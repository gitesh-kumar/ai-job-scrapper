import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import json
from datetime import datetime

# ------------------------ Telegram Setup ------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

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

async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# ------------------------ Individual Scrapers ------------------------
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
            job_type = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title):
                if "full-time" in job_type.lower() or "internship" in job_type.lower():
                    jobs.append(f"{title} at {company} | {link} | {job_type}")
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
            job_type = job_card.find("div", class_="job-type").text.strip() if job_card.find("div", class_="job-type") else ""
            job_id = link
            if job_id not in sent_jobs and job_matches_keywords(title):
                if "full-time" in job_type.lower() or "internship" in job_type.lower():
                    jobs.append(f"{title} at {company} | {link} | {job_type}")
                    sent_jobs.add(job_id)
    except Exception as e:
        asyncio.run(send_telegram_message(f"⚠️ Could not scrape StepStone: {e}"))
    return jobs

# ------------------------ Combine All Sites ------------------------
def scrape_all_sites():
    all_jobs = []
    all_jobs.extend(scrape_datacareer())
    all_jobs.extend(scrape_stepstone())
    # You can add more scrapers here (Indeed, Glassdoor, StackOverflow)
    return all_jobs

# ------------------------ Main ------------------------
async def main():
    now = datetime.now()
    if 8 <= now.hour <= 18:
        new_jobs = scrape_all_sites()
        if new_jobs:
            message = "🧑‍💻 Latest AI/ML Jobs in Germany:\n\n" + "\n".join(new_jobs[:10])
            await send_telegram_message(message)
        # Save sent jobs
        with open(SENT_FILE, "w") as f:
            json.dump(list(sent_jobs), f)

# ------------------------ Run Script ------------------------
if __name__ == "__main__":
    asyncio.run(main())
