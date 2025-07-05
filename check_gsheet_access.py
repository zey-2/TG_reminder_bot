import os
import gspread
from dotenv import load_dotenv
from pathlib import Path

# Explicitly specify the .env file path
dotenv_path = Path(__file__).parent / ".env"
print(f"Loading environment variables from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path)

# Debug: print raw environment variable values
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
print(f"[DEBUG] SHEET_ID from env: {SHEET_ID}")
print(f"[DEBUG] SERVICE_ACCOUNT_JSON from env: {SERVICE_ACCOUNT_JSON}")

def check_gsheet_access():
    """
    Checks access to the Google Sheet using the service account credentials and prints the first worksheet and first row.
    Exits if credentials or sheet ID are missing or access fails.
    """
    if not SHEET_ID or not SERVICE_ACCOUNT_JSON:
        print("Missing GOOGLE_SHEET_ID or GOOGLE_SERVICE_ACCOUNT_JSON in .env")
        exit(1)
    try:
        gc = gspread.service_account(filename=Path(SERVICE_ACCOUNT_JSON))
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.sheet1
        print(f"Successfully accessed Google Sheet: {sh.title}")
        print(f"First worksheet: {worksheet.title}")
        print(f"First row: {worksheet.row_values(1)}")
    except Exception as e:
        print(f"Failed to access Google Sheet: {e}")

if __name__ == "__main__":
    check_gsheet_access()
