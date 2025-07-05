# populate_modules.py
"""
This script clears the 'modules' table and inserts the latest module information into the database.
Run this script before starting the bot to ensure module info is up to date.
"""
import sqlite3
import logging
from config import SQLITE_DB_PATH

MODULES = [
    {
        "module_name": "Foundations of Data Science: Python and SQL",
        "course_run_id": "1135652",
        "course_run_code": "RA576069",
        "attendance_url": "https://www.myskillsfuture.gov.sg/api/take-attendance/RA576069",
        "qr_code_url": "https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576069",
        "start_date": "2025-07-01",
        "end_date": "2025-08-03"
    },
    {
        "module_name": "Scalable Data Solutions: Big Data Engineering Essentials",
        "course_run_id": "1135657",
        "course_run_code": "RA576073",
        "attendance_url": "https://www.myskillsfuture.gov.sg/api/take-attendance/RA576073",
        "qr_code_url": "https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576073",
        "start_date": "2025-08-04",
        "end_date": "2025-09-14"
    },
    {
        "module_name": "Building Intelligent Systems: Machine Learning and Generative AI",
        "course_run_id": "1135662",
        "course_run_code": "RA576079",
        "attendance_url": "https://www.myskillsfuture.gov.sg/api/take-attendance/RA576079",
        "qr_code_url": "https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576079",
        "start_date": "2025-09-15",
        "end_date": "2025-10-19"
    },
    {
        "module_name": "Certified AI Practitioner",
        "course_run_id": "1135673",
        "course_run_code": "RA576096",
        "attendance_url": "https://www.myskillsfuture.gov.sg/api/take-attendance/RA576096",
        "qr_code_url": "https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576096",
        "start_date": "2025-10-20",
        "end_date": "2025-10-26"
    },
    {
        "module_name": "Transforming Business with GPT: Hands-On Generative AI Applications",
        "course_run_id": "1135676",
        "course_run_code": "RA576098",
        "attendance_url": "https://www.myskillsfuture.gov.sg/api/take-attendance/RA576098",
        "qr_code_url": "https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576098",
        "start_date": "2025-10-27",
        "end_date": "2025-11-09"
    },
    {
        "module_name": "Full Stack Programming and Deployment​ of AI Solutions",
        "course_run_id": "1135690",
        "course_run_code": "RA576102",
        "attendance_url": "https://www.myskillsfuture.gov.sg/api/take-attendance/RA576102",
        "qr_code_url": "https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576102",
        "start_date": "2025-11-10",
        "end_date": "2025-11-23"
    },
]

def ensure_qr_code_column(cursor):
    # Check if qr_code_url, start_date, end_date columns exist, add if not (SQLite)
    cursor.execute("PRAGMA table_info(modules)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'qr_code_url' not in columns:
        logging.info("Adding qr_code_url column to modules table...")
        cursor.execute("ALTER TABLE modules ADD COLUMN qr_code_url TEXT")
        logging.info("qr_code_url column added.")
    else:
        logging.info("qr_code_url column already exists.")
    if 'start_date' not in columns:
        logging.info("Adding start_date column to modules table...")
        cursor.execute("ALTER TABLE modules ADD COLUMN start_date TEXT")
        logging.info("start_date column added.")
    else:
        logging.info("start_date column already exists.")
    if 'end_date' not in columns:
        logging.info("Adding end_date column to modules table...")
        cursor.execute("ALTER TABLE modules ADD COLUMN end_date TEXT")
        logging.info("end_date column added.")
    else:
        logging.info("end_date column already exists.")

def populate_modules():
    """
    Clears the 'modules' table and inserts the latest module information into the database.
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        ensure_qr_code_column(cursor)
        # Clear the table
        cursor.execute("DELETE FROM modules")
        # Insert modules
        for m in MODULES:
            cursor.execute(
                """
                INSERT INTO modules (module_name, course_run_id, course_run_code, attendance_url, qr_code_url, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (m["module_name"], m["course_run_id"], m["course_run_code"], m["attendance_url"], m["qr_code_url"], m["start_date"], m["end_date"])
            )
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Modules table has been reset and populated.")
    except Exception as e:
        logging.error(f"Error populating modules table: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    populate_modules()
