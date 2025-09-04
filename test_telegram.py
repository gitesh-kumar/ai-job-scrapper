import os
import asyncio
from telegram import Bot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
bot = Bot(token=TOKEN)

async def send_test_message():
    await bot.send_message(chat_id=CHAT_ID, text="✅ GitHub Actions Telegram test successful!")

asyncio.run(send_test_message())
