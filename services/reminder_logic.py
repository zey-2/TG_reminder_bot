import logging
from datetime import datetime, timedelta
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TIMEZONE
from services.sheet_service import fetch_activities, clean_activities_data
from services.database import get_db_connection, cleanup_duplicate_telegram_ids
from services.scheduler_service import schedule_reminder, clear_reminder_jobs
from utils.message_templates import REMINDER_TEMPLATES, MATERIAL_TEMPLATE
import pytz

def get_active_users():
    """
    Retrieve a list of active Telegram user IDs from the database.
    Returns:
        list: List of active user Telegram IDs.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id FROM users WHERE is_active=1")
    users = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return users

import asyncio
from telegram import Bot

async def schedule_all_reminders(bot: Bot, test_mode=False):
    """
    Schedule reminders for all upcoming activities for all active users.
    Args:
        bot (Bot): Telegram Bot instance.
        test_mode (bool): If True, only schedule a single test reminder for the first valid activity.
    """
    # Clear existing reminder jobs before scheduling new ones
    clear_reminder_jobs()
    
    cleanup_duplicate_telegram_ids()
    raw_values = fetch_activities()
    cleaned = clean_activities_data(raw_values)
    users = get_active_users()
    now = datetime.now(pytz.timezone(TIMEZONE))
    first_valid_activity_processed = False
    for idx, row in enumerate(cleaned):
        title = row.get("Title") or row.get("Lesson Title") or row.get("Unit") or "Activity"
        start_str = row.get("StartTime")
        end_str = row.get("EndTime")
        github_url = row.get("GitHub URL")
        description = row.get("Description", "")
        if not (start_str and end_str):
            continue
        try:
            start_dt = pytz.timezone(TIMEZONE).localize(datetime.strptime(start_str, "%d/%m/%Y %H:%M:%S"))
            end_dt = pytz.timezone(TIMEZONE).localize(datetime.strptime(end_str, "%d/%m/%Y %H:%M:%S"))
        except Exception as e:
            logging.warning(f"Failed to parse StartTime/EndTime: {start_str}, {end_str}: {e}")
            continue

        if end_dt < now:
            continue

        # TEST MODE: Only schedule ONE test message for the first VALID activity
        if test_mode and not first_valid_activity_processed:
            first_valid_activity_processed = True
            logging.warning(f"[TEST MODE] Scheduling ONE test reminder for the first valid activity (index {idx}): {title}")
            test_time = now + timedelta(minutes=1)
            
            async def test_callback():
                """
                Async callback to send a test reminder message to all users for the first valid activity.
                """
                logging.warning(f"[TEST MODE] Sending test reminder for: {title}")
                msg = f"🧪 TEST MODE: {REMINDER_TEMPLATES['start'].format(title=title)}"
                msg += f"\nTime: {start_str} - {end_str}"
                if row.get("Location", ""):
                    msg += f"\nVenue: {row.get('Location', '')}"
                if description:
                    msg += f"\n{description}"
                if github_url:
                    msg += f"\n{MATERIAL_TEMPLATE.format(title=title, github_url=github_url)}"
                msg += f"\n\n📊 In normal mode, this activity would generate 2 reminders: 30min_before, end"
                
                for user_id in users:
                    try:
                        await bot.send_message(chat_id=user_id, text=msg)
                        logging.info(f"[TEST MODE] Test message sent to user {user_id}")
                    except Exception as e:
                        logging.warning(f"Failed to send test reminder to {user_id}: {e}")

                module_info = get_module_by_dates(start_str.split()[0])
                if module_info:
                    msg = ""
                    msg += f"\n\nModule: {module_info['module_name']}"
                    msg += f"\n\nAttendance URL: [{module_info['attendance_url']}]({module_info['attendance_url']})"
                    msg += f"\nQR Code URL: [{module_info['qr_code_url']}]({module_info['qr_code_url']})"

                    for user_id in users:
                        try:
                            await bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
                        except Exception as e:
                            logging.warning(f"Failed to send reminder to {user_id}: {e}")

            print(f"[TEST MODE] Scheduling single test reminder for: {title} at {test_time}")
            schedule_reminder(test_time, test_callback)
            break

        if not start_dt or not end_dt or end_dt < now or (start_dt - now).days > 1:
            continue

        # Schedule reminders
        reminder_times = {
            "30min_before": start_dt - timedelta(minutes=30),
            "end": end_dt,
        }
        for rtype, rtime in reminder_times.items():
            if rtime < now:
                continue
            async def callback(title=title, github_url=github_url, rtype=rtype, start_str=start_str, end_str=end_str, location=row.get("Location", "")):
                """
                Async callback to send a scheduled reminder message to all users for a specific activity and reminder type.
                Args:
                    title (str): Activity title.
                    github_url (str): GitHub URL for materials.
                    rtype (str): Reminder type (e.g., '30min_before', 'end').
                    start_str (str): Start time string.
                    end_str (str): End time string.
                    location (str): Activity location.
                """
                logging.warning(f"[DEBUG] Sending reminder: rtype={rtype}, title={title}, time={rtime}, users={users}")
                msg = REMINDER_TEMPLATES[rtype].format(title=title)
                msg += f"\nTime: {start_str} - {end_str}"
                if location:
                    msg += f"\nVenue: {location}"
                if description:
                    msg += f"\n{description}"
                if github_url:
                    msg += f"\n{MATERIAL_TEMPLATE.format(title=title, github_url=github_url)}"

                for user_id in users:
                    try:
                        await bot.send_message(chat_id=user_id, text=msg)
                    except Exception as e:
                        logging.warning(f"Failed to send reminder to {user_id}: {e}")

                # Add attendance and QR code URLs if module found
                module_info = get_module_by_dates(start_str.split()[0])
                if module_info:
                    msg = ""
                    msg += f"\n\nModule: {module_info['module_name']}"
                    msg += f"\n\nAttendance URL: [{module_info['attendance_url']}]({module_info['attendance_url']})"
                    msg += f"\nQR Code URL: [{module_info['qr_code_url']}]({module_info['qr_code_url']})"

                    for user_id in users:
                        try:
                            await bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
                        except Exception as e:
                            logging.warning(f"Failed to send reminder to {user_id}: {e}")

            # Schedule the async callback using the scheduler (must support async jobs)
            schedule_reminder(rtime, callback)
            
def get_module_by_dates(activity_date):
    """
    Retrieve module information (name, attendance URL, QR code URL) for a given activity date.
    Args:
        activity_date (str): Date string in 'DD/MM/YYYY' or 'YYYY-MM-DD' format.
    Returns:
        dict or None: Module info dict if found, else None.
    """
    # Ensure activity_date is in YYYY-MM-DD format
    try:
        dt = datetime.strptime(activity_date, "%d/%m/%Y")
        activity_date_str = dt.strftime("%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(activity_date, "%Y-%m-%d")
            activity_date_str = activity_date
        except Exception as e:
            logging.warning(f"Invalid activity_date format: {activity_date}: {e}")
            return None

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT module_name, attendance_url, qr_code_url FROM modules
        WHERE ? BETWEEN start_date AND end_date
    """, (activity_date_str,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return {"module_name": result[0], "attendance_url": result[1], "qr_code_url": result[2]}
    return None
