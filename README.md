# DS2 Reminder Bot

A Telegram bot that sends automated reminders and provides course materials for NTU Data Science & AI classes, using a Google Sheet as the source of schedule and activity data.

## Bot Functionality Overview

### Core Features

1. **Google Sheets Integration**
   - Check shared Google Sheet for scheduled classes and activities
   - Sheet URL: https://docs.google.com/spreadsheets/d/17FYhR7zrvSVvf4N3EqaxpfFWMn9opm9jRRV-psBZ4yI/edit?gid=704234018#gid=704234018
   - Sheet ID: 17FYhR7zrvSVvf4N3EqaxpfFWMn9opm9jRRV-psBZ4yI
   - Timezone: Asia/Singapore
   - Monitor course schedules for all 6 modules
   - The Google Sheet is expected to update regularly. The bot will check for changes every day and always use the latest data for scheduling and notifications.
2. **Automated Reminder System**
   - Check Google Sheet periodically for upcoming activities
   - Parse sheet rows to extract class/activity information and timing
   - Send reminder 30 minutes before class starts
   - Send reminder at the end of the lesson with attendance scanning notice
   - All notifications are sent automatically based on sheet schedule
3. **Attendance Management**
   - Provide attendance QR code links for each module
   - Send course-specific attendance instructions
   - Handle both online and physical class attendance scenarios
4. **Course Materials Management**
   - Respond to requests for course materials
   - Provide module-specific information and links

## ⏰ Reminder Scheduling Logic

- **Reminders are now scheduled at two key times:**

  1. **On Bot Startup:** The bot fetches the latest Google Sheet data and schedules all reminders for upcoming activities.
  2. **Daily at 23:00 (Asia/Singapore time):** The bot automatically refreshes the schedule by re-fetching the Google Sheet and rescheduling all reminders for the next day. This ensures new activities are captured and old ones are removed.

- **How It Works:**

  - On startup and every day at 23:00, the bot:
    - Fetches all activities from the Google Sheet.
    - Clears all previously scheduled reminder jobs (to avoid duplicates).
    - Schedules 2 reminders per activity: 30 minutes before and at end.
    - Each reminder is sent to all active users.
  - If the bot is started in test mode, only a single test reminder is scheduled for the first valid activity.

- **Technical Details:**

  - Uses APScheduler’s `CronTrigger` for daily scheduling.
  - All scheduling and time calculations are timezone-aware (Asia/Singapore).
  - Reminder jobs are uniquely managed to prevent duplicate notifications.

- **Relevant Files:**
  - `main.py` — Sets up the daily schedule and startup refresh.
  - `services/scheduler_service.py` — Manages scheduling, clearing, and daily jobs.
  - `services/reminder_logic.py` — Handles fetching, parsing, and scheduling reminders.

## Course Modules and Attendance Links

### Module Information

Each module has specific attendance requirements and QR code generation links:

**Module 1 – Foundations of Data Science: Python and SQL**

- Course Run ID: 1135652
- Course Run Code: RA576069
- Attendance URL: https://www.myskillsfuture.gov.sg/api/take-attendance/RA576069
- QR Code Generator: https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576069

**Module 2 – Scalable Data Solutions: Big Data Engineering Essentials**

- Course Run ID: 1135657
- Course Run Code: RA576073
- Attendance URL: https://www.myskillsfuture.gov.sg/api/take-attendance/RA576073
- QR Code Generator: https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576073

**Module 3 – Building Intelligent Systems: Machine Learning and Generative AI**

- Course Run ID: 1135662
- Course Run Code: RA576079
- Attendance URL: https://www.myskillsfuture.gov.sg/api/take-attendance/RA576079
- QR Code Generator: https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576079

**Module 4 – Certified AI Practitioner**

- Course Run ID: 1135673
- Course Run Code: RA576096
- Attendance URL: https://www.myskillsfuture.gov.sg/api/take-attendance/RA576096
- QR Code Generator: https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576096

**Module 5 – Transforming Business with GPT: Hands-On Generative AI Applications**

- Course Run ID: 1135676
- Course Run Code: RA576098
- Attendance URL: https://www.myskillsfuture.gov.sg/api/take-attendance/RA576098
- QR Code Generator: https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576098

**Module 6 – Full Stack Programming and Deployment of AI Solutions**

- Course Run ID: 1135690
- Course Run Code: RA576102
- Attendance URL: https://www.myskillsfuture.gov.sg/api/take-attendance/RA576102
- QR Code Generator: https://www.myskillsfuture.gov.sg/spface/spverify/scanQRCode?courseRunCode=RA576102

## Attendance Instructions and Bot Messages

### For Online Classes (Synchronous/Asynchronous)

The bot should send instructions for self-scanning:

1. Visit the respective module attendance link
2. Key in the given course run code to generate unique dynamic QR code
3. Complete the attendance scanning process

### For Physical Classes (Face-to-Face - Saturdays)

The bot should inform students that:

1. Physical classes take place on Saturdays
2. Trainer will share the SSG Attendance QR code in class
3. Students must scan the QR code during class time
4. QR code is generated 30 minutes before class and valid until 30 minutes after class ends

### Important Attendance Rules

- All students must scan QR code or be marked ABSENT by SSG
- Technical issues with SSG website require email with error screenshot to Course Admin
- Other reasons for missing attendance require appeal submission to SSG
- Training provider cannot manually upload attendance

## Bot Commands and Responses

### Reminder Messages

1. **30 minutes before class**: "Reminder: Activity ([Calendar title]) starts in 30 minutes. Remember to scan attendance QR code."
2. **Class end**: "Activity ([Calendar title]) has ended. You have 30 minutes to scan for attendance if you haven't done so."

### Material Requests

When users request materials, the bot should provide:

- Module-specific attendance links
- Course run codes
- Instructions for QR code generation
- Contact information for technical issues

## Technical Requirements

### Dependencies

- python-telegram-bot library for Telegram Bot API integration
- gspread and Google Sheets API integration
- Scheduling library (e.g., APScheduler)
- sqlite3 (Python standard library) for SQLite database connections (no external server required)
- Database for storing user preferences and module information

### Configuration

- Telegram Bot Token
- Google Sheets API credentials (Service Account or OAuth2)
  - Shared Sheet ID: 17FYhR7zrvSVvf4N3EqaxpfFWMn9opm9jRRV-psBZ4yI
  - Timezone: Asia/Singapore
- Course schedule data
- Module information and attendance links

### Environment Variables (.env)

- All sensitive configuration (bot token, database credentials, Google API keys, etc.) should be stored in a `.env` file at the project root.
- Use the `python-dotenv` package to load environment variables in your code.

**Example .env file:**

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
GOOGLE_SHEET_ID=17FYhR7zrvSVvf4N3EqaxpfFWMn9opm9jRRV-psBZ4yI
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/service_account.json
TIMEZONE=Asia/Singapore
SQLITE_DB_PATH=bot_database.sqlite3
CHECK_SHEET_INTERVAL=300
```

- Do not commit your `.env` or credentials files to version control.

### Configuration and Credentials Storage

- **Configuration File:**
  - All bot, database, and scheduling settings are stored in `config.py` at the project root (`telegram_reminder_bot/config.py`).
  - This file contains variables such as the Telegram Bot Token, Google Sheet ID, timezone, SQLite database file path, and scheduling intervals.
- **Credentials File:**
  - Google API service account credentials are stored in `credentials/service_account.json`.
  - This file should be kept secure and is required for authenticating with the Google Sheets API.

## Program Architecture

### System Overview

The Telegram bot follows a modular architecture with these core components:

1. **Main Bot Application** - Entry point and Telegram API integration
2. **Sheet Service** - Google Sheets monitoring and activity parsing
3. **Scheduler Service** - Reminder scheduling and execution
4. **Database Layer** - SQLite data persistence
5. **Message Handler** - User interaction and response generation

### Key Components

#### 1. Main Bot (`main.py`)

- Initialize python-telegram-bot
- Set up command handlers (/start, material requests)
- Start polling for messages
- Coordinate between services

#### 2. Sheet Service (`sheet_service.py`)

- Authenticate with Google Sheets API using service account
- Fetch activity rows from shared sheet
- Parse row details: title, start/end times, module information
- Detect new/modified/cancelled activities

#### 3. Scheduler Service (`scheduler_service.py`)

- Use APScheduler for reminder management
- Schedule 2 reminders per activity:
  - 30 minutes before class
  - At class end time
- Handle timezone conversion (Asia/Singapore)
- Cancel/update reminders when activities change

#### 4. Database Layer (`database.py`)

- SQLite connection using sqlite3 (Python standard library)
- Store users, events, modules, and reminder history
- Track which reminders have been sent
- Log user interactions and system events

#### 5. Message Templates (`message_templates.py`)

- Predefined message formats for different reminder types
- Module-specific attendance information
- Error messages and help text

### Database Schema

**Tables:**

- `users` - Telegram user registration and preferences
- `modules` - Course module information with attendance links
- `events` - Calendar events with timing and module mapping
- `reminders` - Scheduled reminder tracking and status
- `logs` - System activity and error logging

### File Structure

```
telegram_reminder_bot/
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── services/
│   ├── sheet_service.py
│   ├── scheduler_service.py
│   └── database.py
├── handlers/
│   └── bot_handlers.py
├── utils/
│   └── message_templates.py
└── credentials/
    └── service_account.json
```

### Data Flow

1. **Sheet Monitoring**: Check sheet → Parse activities → Update database → Schedule reminders
2. **Reminder Execution**: Scheduler triggers → Load activity data → Send messages → Log status
3. **User Interaction**: Receive message → Process request → Query database → Send response

### Google Sheet Structure and Parsing

The bot expects the Google Sheet to have the following columns (or similar):

- **Date**: Date of the activity
- **Title**: Name/description of the activity
- **Start**: Start time (e.g., 19:00)
- **End**: End time (e.g., 22:00)
- **StartTime**: Calculated start time in minutes from midnight
- **EndTime**: Calculated end time in minutes from midnight
- **Location**: Venue or online platform
- **Description**: Additional details or material links

#### Example Row:

| Date       | Title                               | Start | End   | StartTime | EndTime | Location    | Description                         |
| ---------- | ----------------------------------- | ----- | ----- | --------- | ------- | ----------- | ----------------------------------- |
| 2025-07-01 | Welcome + Introduction + Onboarding | 19:00 | 22:00 |           |         | Online Zoom | https://github.com/example/material |

#### Parsing Logic (Actual Script):

- The bot fetches all rows from the Google Sheet and parses each row as an activity or event.
- It uses the "Date", "Title", "Start", "End", "StartTime", "EndTime", and "Location" columns to determine the schedule and timing of each activity.
- The "Title" is used as the main activity name in reminders and notifications.
- The "Description" column is used for additional details and, if it contains a URL, is treated as the "GitHub URL" for material links.
- The bot schedules multiple reminders for each activity: 30 minutes before, at start, at midpoint, at end, and 30 minutes after end.
- All date and time parsing is done in the Asia/Singapore timezone.
- The bot updates or cancels reminders if the sheet data changes.

This structure allows the bot to flexibly support a variety of activity types and provide rich, context-aware reminders and responses.
