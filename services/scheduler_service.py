from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import logging

scheduler = AsyncIOScheduler()

def schedule_reminder(dt, callback, args=None):
    """
    Schedule a one-time reminder job to run at the specified datetime.
    Args:
        dt (datetime): The date and time to run the job.
        callback (callable): The function or coroutine to call.
        args (list, optional): Arguments to pass to the callback.
    """
    scheduler.add_job(
        callback,
        trigger=DateTrigger(run_date=dt),
        args=args or [],
        misfire_grace_time=60,  # Allow job to run if missed by up to 60 seconds
        coalesce=True  # Coalesce multiple missed runs into one
    )

def schedule_daily_job(hour, minute, callback, args=None, timezone_str="Asia/Singapore"):
    """
    Schedule a job to run daily at the specified hour and minute.
    Args:
        hour (int): Hour of the day (0-23).
        minute (int): Minute of the hour (0-59).
        callback (callable): The function or coroutine to call.
        args (list, optional): Arguments to pass to the callback.
        timezone_str (str): Timezone string.
    """
    scheduler.add_job(
        callback,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone_str),
        args=args or [],
        misfire_grace_time=300,  # Allow job to run if missed by up to 5 minutes
        coalesce=True,
        id="daily_reminder_refresh"  # Unique ID to prevent duplicates
    )

def clear_reminder_jobs():
    """
    Clear all scheduled reminder jobs except the daily refresh job.
    """
    jobs_to_remove = []
    for job in scheduler.get_jobs():
        if job.id != "daily_reminder_refresh":
            jobs_to_remove.append(job.id)
    
    for job_id in jobs_to_remove:
        scheduler.remove_job(job_id)
    
    logging.info(f"Cleared {len(jobs_to_remove)} existing reminder jobs")

def start_scheduler():
    """
    Start the APScheduler if it is not already running.
    """
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler started.")

def stop_scheduler():
    """
    Stop the APScheduler if it is running.
    """
    if scheduler.running:
        scheduler.shutdown()
        logging.info("Scheduler stopped.")
