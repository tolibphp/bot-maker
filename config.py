import os
from dotenv import load_dotenv

load_dotenv()

# Master Bot
MASTER_TOKEN = os.getenv("MASTER_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Admin info
ADMIN_USERNAME = "@halol_bolakay"
PAYMENT_CARD = os.getenv("PAYMENT_CARD", "0000 0000 0000 0000")
PAYMENT_CARD_HOLDER = os.getenv("PAYMENT_CARD_HOLDER", "Ism Familiya")

# Database
DB_PATH = os.getenv("DB_PATH", "data")

# Prices (in so'm)
BOT_CREATE_PRICE = 35_000
DAILY_FEE = 5_000
FREE_TRIAL_DAYS = 30

# Bot templates
TEMPLATES = {
    "kino": {"name": "🎬 Kino Bot", "price": 30_000, "module": "kino_bot", "daily_price": 5000},
    "stars": {"name": "⭐️ Stars Referral Bot", "price": 15_000, "module": "stars_bot", "daily_price": 2000},
    "money": {"name": "💸 Premium Pul Ishlash", "price": 15_000, "module": "money_bot", "daily_price": 2000},
    "downloader": {"name": "📥 Video Yuklovchi Bot", "price": 15_000, "module": "downloader_bot", "daily_price": 2000}
}
