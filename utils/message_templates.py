"""
Templates for reminder and material messages used by the Telegram bot.
"""

REMINDER_TEMPLATES = {
    "30min_before": "Reminder: Activity ({title}) starts in 30 minutes. Remember to scan attendance QR code.",
    "start": "Activity ({title}) is starting now. Don't forget to scan attendance QR code if required.",
    "mid": "Mid-activity reminder: {title} is in progress.",
    "end": "Activity ({title}) has ended. You have 30 minutes to scan for attendance if you haven't done so.",
    "30min_after": "Final reminder: Only a few minutes left to scan attendance for {title}."
}

MATERIAL_TEMPLATE = "Materials for {title}: {github_url}"
