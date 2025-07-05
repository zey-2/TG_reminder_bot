from telegram import Update, BotCommand
from telegram.ext import CommandHandler, ContextTypes
from services.database import get_db_connection, cleanup_duplicate_telegram_ids
from config import GOOGLE_SHEET_ID
from datetime import datetime
import pytz
from services.sheet_service import fetch_activities, clean_activities_data

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command. Registers the user and sends a welcome message.
    """
    if update.message:
        await update.message.reply_text(
            "Welcome to the DS2 Reminder Bot!\n"
            "You will receive reminders and materials automatically.\n"
            "The bot checks the Google Sheet daily and sends 2 reminders per activity (30 mins before the start & end).\n"
            "You may retrieve some useful materials related to our course using the commands.\n"
            "It will be nice to mute this bot in order not to affect the lesson.\n"
            "If you wish to stop or resume reminders, use /toggle_reminder."
        )
    # Ensure user is active by default
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = update.effective_user.id if update.effective_user else None
    username = update.effective_user.username if update.effective_user else None
    cursor.execute(
        "INSERT OR REPLACE INTO users (telegram_id, username, registration_date, is_active) VALUES (?, ?, datetime('now'), 1)",
        (user_id, username)
    )
    conn.commit()
    cursor.close()
    conn.close()

async def toggle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /toggle_reminder command. Enables or disables reminders for the user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = update.effective_user.id if update.effective_user else None
    username = update.effective_user.username if update.effective_user else None
    cursor.execute("SELECT is_active FROM users WHERE telegram_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            "INSERT INTO users (telegram_id, username, registration_date, is_active) VALUES (?, ?, datetime('now'), 0)",
            (user_id, username)
        )
        conn.commit()
        if update.message:
            await update.message.reply_text("Reminders are now disabled. Use /toggle_reminder to enable them again.")
    else:
        new_status = 0 if row[0] else 1
        cursor.execute("UPDATE users SET is_active=? WHERE telegram_id=?", (new_status, user_id))
        conn.commit()
        if update.message:
            if new_status:
                await update.message.reply_text("Reminders are now enabled. You will receive notifications.")
            else:
                await update.message.reply_text("Reminders are now disabled. You will not receive notifications.")
    cursor.close()
    conn.close()

# /req_schedule command
async def req_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /req_schedule command. Sends the Google Sheet schedule link to the user.
    """
    if update.message:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit"
        await update.message.reply_text(
            f"📅 DS2 Schedule\n\n"
            f"Here's the link to our Google Sheet schedule:\n"
            f"{sheet_url}\n\n"
            f"This contains all upcoming activities, timings, and details for our Data Science & AI course."
        )


# /recent command
async def recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /recent command. Shows the next 5 upcoming activities to the user.
    """
    if update.message:
        try:
            # Fetch and clean activities from Google Sheet
            raw_activities = fetch_activities()
            activities = clean_activities_data(raw_activities)
            
            # Filter and sort upcoming activities
            now = datetime.now(pytz.timezone('Asia/Singapore'))
            upcoming_activities = []
            
            for activity in activities:
                start_str = activity.get("StartTime")
                if start_str:
                    try:
                        start_dt = pytz.timezone('Asia/Singapore').localize(
                            datetime.strptime(start_str, "%d/%m/%Y %H:%M:%S")
                        )
                        if start_dt > now:
                            upcoming_activities.append((start_dt, activity))
                    except Exception:
                        continue
            
            # Sort by start time and take first 5
            upcoming_activities.sort(key=lambda x: x[0])
            upcoming_activities = upcoming_activities[:5]
            
            if upcoming_activities:
                message = "📍 Next 5 Upcoming Activities:\n\n"
                for i, (start_dt, activity) in enumerate(upcoming_activities, 1):
                    title = activity.get("Title", "Activity")
                    location = activity.get("Location", "TBD")
                    start_time = start_dt.strftime("%d/%m/%Y %H:%M")
                    end_str = activity.get("EndTime", "")
                    
                    message += f"{i}. {title}\n"
                    message += f"   📅 {start_time}"
                    if end_str:
                        try:
                            end_dt = pytz.timezone('Asia/Singapore').localize(
                                datetime.strptime(end_str, "%d/%m/%Y %H:%M:%S")
                            )
                            message += f" - {end_dt.strftime('%H:%M')}"
                        except Exception:
                            pass
                    message += f"\n   📍 {location}\n\n"
                
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("📅 No upcoming activities found in the schedule.")
        except Exception as e:
            await update.message.reply_text("❌ Unable to fetch schedule. Please try again later.")

# /broadcast command (hidden - admin only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /broadcast command. Sends a broadcast message to all users.
    """
    if update.message:
        # Cleanup duplicates before broadcasting
        cleanup_duplicate_telegram_ids()
        user_id = update.effective_user.id if update.effective_user else None
        
        # Check if message has arguments
        if not context.args:
            await update.message.reply_text("📢 Usage: /broadcast <message>")
            return
        
        # Join all arguments to form the broadcast message
        broadcast_message = " ".join(context.args)
        
        # Get all unique users from database (including the broadcaster)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT telegram_id FROM users")
        all_users = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        if not all_users:
            await update.message.reply_text("No users found in database.")
            return
        
        # Send broadcast message to all users
        success_count = 0
        fail_count = 0
        
        for target_user_id in all_users:
            try:
                await context.bot.send_message(
                    chat_id=target_user_id, 
                    text=f"📢 Broadcast Message:\n\n{broadcast_message}"
                )
                success_count += 1
            except Exception as e:
                fail_count += 1
        
        # Send summary to broadcaster
        await update.message.reply_text(
            f"📊 Broadcast Summary:\n"
            f"✅ Successfully sent: {success_count}\n"
            f"❌ Failed to send: {fail_count}\n"
            f"📱 Total users: {len(all_users)}"
        )

# /wifi command
async def wifi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /wifi command. Provides instructions for NTU Wireless Network Login.
    """
    if update.message:
        await update.message.reply_text(
            "📶 NTU Wireless Network Login\n\n"
            "1. If you have an NTU Learn account, you can connect to the NTUSECURE WiFi using your NTU credentials. "
            "You do not need to request for guest credentials each time you want to login.\n\n"
            "2. For guest access:\n"
            "   - SMS the word `register` to 93722830 to get free WiFi access for the day.\n"
            "   - A username and password will be sent to you via SMS.\n"
            "   - Select wireless network: NTUGUEST.\n"
            "   - Open your web browser (IE, Firefox, Safari). You will be directed to the login page.\n"
            "   - Key in:\n"
            "     * User Name: Your phone number\n"
            "     * Password: The password received via SMS\n"
            "       (Note: Password is case sensitive. Do not share your username and password with others.)\n"
            "   - Domain: GUEST\n"
            "   - Click Submit."
        )

# /direction_ntu command
async def direction_ntu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /direction_ntu command. Sends the directions to NTU@one-north Executive Centre.
    """
    if update.message:
        await update.message.reply_document(
            document=open("materials/Directions to NTU@one-north Executive Centre.pdf", "rb"),
            caption="📍 Directions to NTU@one-north Executive Centre"
        )

# /direction_e2i command
async def direction_e2i(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /direction_e2i command. Sends the directions to e2i@Jurong East.
    """
    if update.message:
        await update.message.reply_document(
            document=open("materials/Direction to e2i@Jurong East.pdf", "rb"),
            caption="📍 Directions to e2i@Jurong East"
        )

# /direction_lli command
async def direction_lli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /direction_lli command. Sends the directions to LLI@Paya Lebar.
    """
    if update.message:
        await update.message.reply_document(
            document=open("materials/Directions to LLI@Paya Lebar.pdf", "rb"),
            caption="📍 Directions to LLI@Paya Lebar"
        )

# /feedback command
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /feedback command. Sends feedback or suggestions to the bot creator.
    """
    if update.message:
        await update.message.reply_text(
            "📩 Feedback\n\n"
            "I value your feedback! Please send your suggestions or issues to me (@TanZhiHao)"
        )

# /ntu_learn command
async def ntu_learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /ntu_learn command. Provides the link to NTU Learn for announcements and assessments.
    """
    if update.message:
        await update.message.reply_text(
            "\U0001F4DA NTU Learn\n\n"
            "Access announcements and assessments at NTU Learn:\n"
            "https://ntulearn.ntu.edu.sg/ultra/institution-page"
        )

# /zoom command
async def zoom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /zoom command. Provides the link for the Zoom lesson.
    """
    if update.message:
        await update.message.reply_text(
            "\U0001F4F9 Zoom Lesson Link\n\n"
            "Join the Zoom lesson here:\n"
            "https://ntu-sg.zoom.us/meeting/register/xtJa3RhhQuurKMnBXuqEWg"
        )

async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Start the DS2 Reminder Bot and register for reminders"),
        BotCommand("toggle_reminder", "Enable or disable reminder notifications"),
        BotCommand("req_schedule", "Request the Google Sheet schedule link"),
        BotCommand("recent", "Show next 5 upcoming activities"),
        BotCommand("ntu_learn", "Get the link to NTU Learn for announcements and assessments"),
        BotCommand("zoom", "Get the Zoom lesson link"),
        BotCommand("wifi", "Instructions for NTU Wireless Network Login"),
        BotCommand("direction_ntu", "Get directions to NTU@one-north Executive Centre"),
        BotCommand("direction_e2i", "Get directions to e2i@Jurong East"),
        BotCommand("direction_lli", "Get directions to LLI@Paya Lebar"),
        BotCommand("feedback", "Send feedback or suggestions to the bot creator"),
        
    ]
    await application.bot.set_my_commands(commands)

def get_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("toggle_reminder", toggle_reminder),
        CommandHandler("req_schedule", req_schedule),
        CommandHandler("recent", recent),
        CommandHandler("broadcast", broadcast),
        CommandHandler("ntu_learn", ntu_learn),
        CommandHandler("zoom", zoom),
        CommandHandler("wifi", wifi),
        CommandHandler("direction_ntu", direction_ntu),
        CommandHandler("direction_e2i", direction_e2i),
        CommandHandler("direction_lli", direction_lli),
        CommandHandler("feedback", feedback),
        
    ]
