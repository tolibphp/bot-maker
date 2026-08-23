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
    "kino": {
        "name": "🎬 Kino Bot",
        "description": "Professional kino bot — qidirish, kategoriya, admin panel",
        "price": BOT_CREATE_PRICE,
    }
}
