import logging
import json
import asyncio
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# --- ফ্রী সার্ভার ট্রিক (Render এর জন্য) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- কনফিগারেশন (এখানে আপনার সব এডমিনের আইডি দিন) ---
TOKEN = "8482209684:AAF28PBodz-_aN-1Btf7AczQQxgF1ZafxuY"  # আপনার বোট টোকেন
ADMIN_IDS = [7715549779, 987654321, 11223344]  # কমা দিয়ে একাধিক আইডি লিখুন

DATA_FILE = "bot_data.json"

# --- ফন্ট কনভার্টার ---
def to_serif_bold(text):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
    trans_table = str.maketrans(normal, bold)
    return text.translate(trans_table)

# --- হ্যাকিং লোডিং এফেক্ট ---
async def hack_loading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(to_serif_bold("Loading."))
    for i in range(2): 
        await asyncio.sleep(0.3)
        await msg.edit_text(to_serif_bold("Loading..."))
    return msg

# --- ডেটা লোড/সেভ ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"approved": [], "blocked": [], "pending": [], "old_classes": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- কীবোর্ড ---
def get_admin_keyboard():
    keyboard = [
        [InlineKeyboardButton(to_serif_bold("Add User"), callback_data="admin_add"),
         InlineKeyboardButton(to_serif_bold("Remove User"), callback_data="admin_remove")],
        [InlineKeyboardButton(to_serif_bold("View Users"), callback_data="admin_view")],
        [InlineKeyboardButton(to_serif_bold("Clear Old Classes"), callback_data="admin_clear_class")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_keyboard():
    keyboard = [
        [InlineKeyboardButton(to_serif_bold("Admin Support"), callback_data="user_support"),
         InlineKeyboardButton(to_serif_bold("Old Class"), callback_data="user_old_class")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- কমান্ড হ্যান্ডলার ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    
    loading_msg = await hack_loading(update, context)
    await loading_msg.delete()

    # একাধিক এডমিন চেক
    if user.id in ADMIN_IDS:
        await update.message.reply_text(to_serif_bold(f"Welcome Admin {user.first_name}."), reply_markup=get_admin_keyboard())
        return

    if user.id in data["blocked"]:
        await update.message.reply_text(to_serif_bold("You are blocked."))
        return

    if user.id in data["approved"]:
        await update.message.reply_text(to_serif_bold("Welcome Crew Member."), reply_markup=get_user_keyboard())
    else:
        keyboard = [[InlineKeyboardButton(to_serif_bold("Request Access"), callback_data="request_access")]]
        await update.message.reply_text(to_serif_bold("You do not have permission."), reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = load_data()
    await query.answer()

    if query.data == "request_access":
        if user.id in data["pending"]:
            await query.edit_message_text(to_serif_bold("Request Pending."))
            return
        data["pending"].append(user.id)
        save_data(data)
        await query.edit_message_text(to_serif_bold("Request Sent."))
        
        # সব এডমিনকে নোটিফিকেশন পাঠানো
        keyboard = [[InlineKeyboardButton("Approve", callback_data=f"approve_{user.id}"),
                     InlineKeyboardButton("Decline", callback_data=f"decline_{user.id}")]]
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=f"New Request: {user.first_name} ({user.id})", reply_markup=InlineKeyboardMarkup(keyboard))
            except: pass

    elif query.data == "user_support":
        await context.bot.send_message(chat_id=user.id, text=to_serif_bold("Type your message:"))
        context.user_data['state'] = 'support_mode'

    elif query.data == "user_old_class":
        if not data["old_classes"]:
            await context.bot.send_message(chat_id=user.id, text=to_serif_bold("No classes yet."))
            return
        # সব ওল্ড ক্লাস পাঠানোর সময় একটি নির্দিষ্ট এডমিনের চ্যাট থেকে কপি হবে
        # এখানে ডিফল্ট হিসেবে তালিকার প্রথম এডমিনকে ব্যবহার করা হচ্ছে
        source_chat = ADMIN_IDS[0] 
        await context.bot.send_message(chat_id=user.id, text=to_serif_bold("Sending Old Classes..."))
        for item in data["old_classes"]:
            try: await context.bot.copy_message(chat_id=user.id, from_chat_id=source_chat, message_id=item)
            except: pass

    elif query.data.startswith("approve_"):
        uid = int(query.data.split("_")[1])
        if uid not in data["approved"]:
            data["approved"].append(uid)
            if uid in data["pending"]: data["pending"].remove(uid)
            save_data(data)
            await context.bot.send_message(chat_id=uid, text=to_serif_bold("Approved! Type /start."), reply_markup=get_user_keyboard())
            await query.edit_message_text(to_serif_bold(f"User {uid} Approved by Admin."))
        else: await query.edit_message_text("Already Approved.")

    elif query.data.startswith("decline_"):
        uid = int(query.data.split("_")[1])
        if uid in data["pending"]: data["pending"].remove(uid)
        data["blocked"].append(uid)
        save_data(data)
        await query.edit_message_text(to_serif_bold(f"User {uid} Declined."))

    elif query.data == "admin_view":
        # শুধুমাত্র যে এডমিন বাটন টিপছে তাকে লিস্ট দেখাবে
        await context.bot.send_message(chat_id=user.id, text=f"Users: {data['approved']}")

    elif query.data == "admin_add":
        await context.bot.send_message(chat_id=user.id, text="Send ID to Add:")
        context.user_data['state'] = 'add_user'

    elif query.data == "admin_remove":
        await context.bot.send_message(chat_id=user.id, text="Send ID to Remove:")
        context.user_data['state'] = 'remove_user'

    elif query.data == "admin_clear_class":
        data["old_classes"] = []
        save_data(data)
        await context.bot.send_message(chat_id=user.id, text=to_serif_bold("Old Class history cleared."))

    elif query.data.startswith("save_class_"):
        mid = int(query.data.split("_")[2])
        if mid not in data["old_classes"]:
            data["old_classes"].append(mid)
            save_data(data)
            await query.edit_message_text(to_serif_bold("Saved."))
        else: await query.edit_message_text("Already Saved.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    state = context.user_data.get('state')

    # --- যে কোনো এডমিনের জন্য লজিক ---
    if user.id in ADMIN_IDS:
        if state == 'add_user':
            try:
                uid = int(update.message.text)
                if uid not in data["approved"]:
                    data["approved"].append(uid)
                    save_data(data)
                    await update.message.reply_text("Added.")
                else:
                    await update.message.reply_text("User already exists.")
            except: pass
            context.user_data['state'] = None
            return

        if state == 'remove_user':
            try:
                uid = int(update.message.text)
                if uid in data["approved"]:
                    data["approved"].remove(uid)
                    save_data(data)
                    await update.message.reply_text("Removed.")
            except: pass
            context.user_data['state'] = None
            return

        # Broadcast (এডমিন যা পাঠাবে তা সব ইউজারের কাছে যাবে)
        count = 0
        for uid in data["approved"]:
            try: 
                await update.message.copy(chat_id=uid)
                count += 1
            except: pass
        
        btn = [[InlineKeyboardButton("Yes, Save", callback_data=f"save_class_{update.message.message_id}")]]
        await update.message.reply_text(f"Sent to {count}. Save to Old Class?", reply_markup=InlineKeyboardMarkup(btn))
        return

    # --- ইউজার লজিক ---
    if state == 'support_mode':
        # ইউজারের মেসেজ সব এডমিনের কাছে ফরোয়ার্ড হবে
        for admin_id in ADMIN_IDS:
            try:
                await update.message.forward(chat_id=admin_id)
            except: pass
            
        await update.message.reply_text(to_serif_bold("Sent to Admins."))
        context.user_data['state'] = None

# --- মেইন রানার ---
if __name__ == '__main__':
    # ফ্রী সার্ভার চালু করা (Flask)
    threading.Thread(target=run_web_server).start()

    if not os.path.exists(DATA_FILE):
        save_data({"approved": [], "blocked": [], "pending": [], "old_classes": []})

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()
        
