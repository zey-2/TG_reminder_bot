import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Singapore")
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "bot_database.sqlite3")
CHECK_SHEET_INTERVAL = int(os.getenv("CHECK_SHEET_INTERVAL", 86400))  # Default: 86400 seconds = 1 day
