import logging
import asyncio
from telegram.ext import ApplicationBuilder
from config import TELEGRAM_BOT_TOKEN, TIMEZONE
from handlers.bot_handlers import get_handlers, set_bot_commands
from services.database import ensure_tables
from services.scheduler_service import start_scheduler, schedule_daily_job
from services.reminder_logic import schedule_all_reminders
from populate_modules import populate_modules

logging.basicConfig(
    # level=logging.INFO,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

async def setup_bot(test_mode=False):
    """
    Set up the Telegram bot, initialize database tables, populate modules, add handlers, start the scheduler, schedule reminders, and set bot commands.
    
    Args:
        test_mode (bool): If True, run in test mode (schedules only one test reminder).
    
    Returns:
        application: The Telegram Application instance.
    """
    ensure_tables()
    populate_modules()
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Please check your .env file.")
    
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    for handler in get_handlers():
        application.add_handler(handler)
    
    start_scheduler()
    
    # Schedule reminders on startup
    await schedule_all_reminders(application.bot, test_mode=test_mode)
    logging.info("Bot started and initial reminders scheduled.")
    
    # Schedule daily reminder refresh at 23:00
    async def daily_reminder_refresh():
        """
        Async callback to refresh all reminders daily at the scheduled time.
        """
        logging.info("=== Running daily reminder refresh at 23:00 ===")
        await schedule_all_reminders(application.bot, test_mode=test_mode)
        logging.info("=== Daily reminder refresh completed ===")
    
    schedule_daily_job(23, 0, daily_reminder_refresh, timezone_str=TIMEZONE)
    logging.info(f"Daily reminder refresh scheduled for 23:00 {TIMEZONE} timezone")

    # Set bot commands for Telegram UI
    await set_bot_commands(application)
    
    return application

def main():
    """
    Main entry point for running the bot. Sets up the event loop and starts the bot application.
    """
    try:
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Setup the bot
        import sys
        test_mode = '--test' in sys.argv
        print(f"Running in {'test' if test_mode else 'normal'} mode.")
        application = loop.run_until_complete(setup_bot(test_mode=test_mode))
        
        # Start polling (this will run the event loop)
        application.run_polling()
        
    except KeyboardInterrupt:
        logging.info("Application interrupted by user.")
    finally:
        # Clean up
        if 'loop' in locals():
            loop.close()


if __name__ == "__main__":
    main()
