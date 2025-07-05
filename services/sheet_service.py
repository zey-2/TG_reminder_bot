import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON
from config import GOOGLE_SHEET_NAME

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_gspread_client():
    """
    Returns an authorized gspread client using the service account credentials.
    """
    creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES)
    return gspread.authorize(creds)

def fetch_activities():
    """
    Fetches all values from the specified Google Sheet worksheet.
    Returns:
        list: List of rows from the worksheet.
    """
    client = get_gspread_client()
    if GOOGLE_SHEET_ID is None:
        raise ValueError("GOOGLE_SHEET_ID must not be None.")
    if GOOGLE_SHEET_NAME is None:
        raise ValueError("GOOGLE_SHEET_NAME must not be None.")
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_NAME)
    values = sheet.get_all_values()
    return values

def clean_activities_data(values):
    """
    Cleans and extracts relevant columns from the raw sheet values.
    Returns a list of dicts with keys:
    Course, Date, Title, Start, End, Location, Description, GitHub URL
    Args:
        values (list): Raw values from the worksheet.
    Returns:
        list: List of cleaned activity dictionaries.
    """
    # Find the header row (first row containing all required fields)
    required_fields = ["Date", "Title", "Location", "Start", "End", "StartTime", "EndTime", "Description"]
    header_row_idx = None
    for idx, row in enumerate(values):
        if all(field in row for field in required_fields):
            header_row_idx = idx
            break
    if header_row_idx is None:
        raise ValueError("Header row with all required fields not found.")
    header = values[header_row_idx]
    # Map field name to column index
    col_map = {field: header.index(field) for field in required_fields}

    # Extract data rows
    cleaned = []
    for row in values[header_row_idx+1:]:
        # Skip empty rows
        if not any(row):
            continue
        # Only keep rows with a Title or Description (as a proxy for real lessons)
        title = row[col_map["Title"]] if col_map["Title"] < len(row) else ""
        description = row[col_map["Description"]] if col_map["Description"] < len(row) else ""
        github_url = description if description.startswith("http") else ""
        if not title and not github_url:
            continue
        entry = {
            "Date": row[col_map["Date"]] if col_map["Date"] < len(row) else "",
            "Title": title,
            "Start": row[col_map["Start"]] if col_map["Start"] < len(row) else "",
            "End": row[col_map["End"]] if col_map["End"] < len(row) else "",
            "StartTime": row[col_map["StartTime"]] if col_map["StartTime"] < len(row) else "",
            "EndTime": row[col_map["EndTime"]] if col_map["EndTime"] < len(row) else "",
            "Location": row[col_map["Location"]] if col_map["Location"] < len(row) else "",
            "Description": description,
            "GitHub URL": github_url
        }
        cleaned.append(entry)
    return cleaned
