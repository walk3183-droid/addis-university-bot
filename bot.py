import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "").strip()  # Put your token in .env file
if not TOKEN:
    raise SystemExit("Missing BOT_TOKEN in .env. Add the token you got from @BotFather and restart the bot.")

# ========================== CONFIGURE YOUR RESOURCES HERE ==========================
# Structure: Department -> Year -> List of (Course Name, File Path or URL)
RESOURCES = {
    "Computer Science": {
        "Year 1": [
            ("Introduction to Programming", "pdfs/cs/year1/intro_programming.pdf"),
            ("Calculus I", "pdfs/cs/year1/calculus.pdf"),
        ],
        "Year 2": [
            ("Data Structures", "pdfs/cs/year2/data_structures.pdf"),
            ("Database Systems", "pdfs/cs/year2/database.pdf"),
        ],
        "Year 3": [
            ("Algorithms", "pdfs/cs/year3/algorithms.pdf"),
        ]
    },
    "Electrical Engineering": {
        "Year 1": [
            ("Circuit Theory", "pdfs/ee/year1/circuits.pdf"),
        ],
        "Year 2": [
            ("Digital Electronics", "pdfs/ee/year2/digital.pdf"),
        ]
    },
    "Business Administration": {
        "Year 1": [
            ("Principles of Management", "pdfs/business/year1/management.pdf"),
        ]
    },
    # Add more departments here...
}

# Helper function to create inline keyboard
def get_keyboard(options, prefix=""):
    keyboard = []
    for option in options:
        callback_data = f"{prefix}:{option}" if prefix else option
        keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_keyboard(RESOURCES.keys())
    await update.message.reply_text(
        "🎓 Welcome to Addis University Resources Bot\n\n"
        "Choose your Department:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split(":")

    if len(parts) == 1:  # Department selected
        dept = parts[0]
        context.user_data['dept'] = dept
        years = list(RESOURCES[dept].keys())
        keyboard = get_keyboard(years, prefix=dept)
        
        await query.edit_message_text(
            f"📚 {dept}\nChoose your Year:",
            reply_markup=keyboard
        )

    elif len(parts) == 2:  # Year selected
        dept = parts[0]
        year = parts[1]
        context.user_data['year'] = year
        
        courses = RESOURCES[dept][year]
        keyboard = []
        for course_name, file_path in courses:
            # Using course name as callback (we'll map it later)
            keyboard.append([InlineKeyboardButton(course_name, callback_data=f"file:{dept}:{year}:{course_name}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Years", callback_data=dept)])
        
        await query.edit_message_text(
            f"📖 {dept} - {year}\nChoose the course material:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif len(parts) == 4 and parts[0] == "file":  # File selected
        dept = parts[1]
        year = parts[2]
        course_name = parts[3]
        
        # Find the file path
        courses = RESOURCES[dept][year]
        file_path = next((path for name, path in courses if name == course_name), None)
        
        if file_path and os.path.exists(file_path):
            await query.message.reply_document(
                document=open(file_path, 'rb'),
                filename=os.path.basename(file_path),
                caption=f"📄 {course_name}\n{dept} - {year}"
            )
            await query.answer("✅ File sent!")
        else:
            await query.answer("❌ File not found. Contact admin.", show_alert=True)

            # ========================== MAIN ==========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()