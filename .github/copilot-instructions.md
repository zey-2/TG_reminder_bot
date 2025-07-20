# Copilot Instructions for DS2 Reminder Bot

## Project Architecture

- **main.py**: Entry point. Sets up logging, config, bot handlers, database, scheduler, and reminder logic. Schedules reminders on startup and daily at 23:00 (Asia/Singapore).
- **handlers/**: Contains all Telegram command handlers. Each handler is an async function. Use SQLite parameter style (`?`) for DB queries. Example: `bot_handlers.py`.
- **services/**: Contains business logic and integrations:
  - `database.py`: Table creation, DB connection, user management.
  - `scheduler_service.py`: APScheduler integration for async job scheduling.
  - `reminder_logic.py`: Fetches activities from Google Sheets, parses, and schedules reminders.
  - `sheet_service.py`: Google Sheets API integration.
- **populate_modules.py**: Populates module info and ensures DB schema (including QR code URLs).
- **utils/**: Message templates and reusable helpers.
- **materials/**: PDF resources sent by bot commands.

## Data Flow & Scheduling

- On startup and daily at 23:00, the bot fetches Google Sheet data and schedules reminders for all activities.
- Reminders are sent 30 minutes before and at the end of each activity.
- All time calculations are timezone-aware (Asia/Singapore).
- User registration and status are managed in the `users` table. Use `/start` and `/toggle_reminder` commands.

## Developer Workflows

- **Run the bot:**
  ```cmd
  python main.py
  ```
- **Test mode:**
  ```cmd
  python main.py --test
  ```
- **Logs:**
  - All logs are written to `bot.log` and console.
- **Database:**
  - SQLite file: `bot_database.sqlite3`
  - Tables: `users`, `modules`, `events`, `reminders`, `logs`
- **Google Sheets:**
  - Sheet ID is set in `config.py`.
  - Credentials in `credentials/` (ignored by git).

## Project-Specific Patterns

- **Async everywhere:** All handlers and scheduling logic use async/await.
- **SQLite parameter style:** Always use `?` for query parameters, not `%s`.
- **Upsert pattern:** Use `INSERT OR REPLACE` for user registration.
- **Command registration:** All bot commands are registered in `set_bot_commands` and `get_handlers`.
- **Material sending:** Use `reply_document` for PDFs in `materials/`.
- **Broadcasts:** `/broadcast` command sends to all users, after deduplication.

## Integration Points

- **Telegram Bot API:** All bot logic uses `python-telegram-bot` (async API).
- **Google Sheets API:** For schedule and activity data.
- **APScheduler:** For async job scheduling and daily refresh.

## Example Patterns

- Register user:
  ```python
  cursor.execute("INSERT OR REPLACE INTO users (telegram_id, username, registration_date, is_active) VALUES (?, ?, datetime('now'), 1)", (user_id, username))
  ```
- Schedule daily job:
  ```python
  schedule_daily_job(23, 0, daily_reminder_refresh, timezone_str=TIMEZONE)
  ```
- Send PDF material:
  ```python
  await update.message.reply_document(document=open("materials/Directions to NTU@one-north Executive Centre.pdf", "rb"), caption="Directions")
  ```

## Key Files & Directories

- `main.py`, `handlers/bot_handlers.py`, `services/`, `populate_modules.py`, `materials/`, `utils/`, `config.py`, `requirements.txt`

---

If any section is unclear or missing, please provide feedback to improve these instructions.
