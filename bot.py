import logging
import json
import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# --- কনফিগারেশন ---
TOKEN = "8482209684:AAF28PBodz-_aN-1Btf7AczQQxgF1ZafxuY"  # আপনার বোট টোকেন
ADMIN_ID = 7715549779           # আপনার টেলিগ্রাম আইডি

# --- ফাইল সেটআপ ---
DATA_FILE = "bot_data.json"

# --- ফন্ট কনভার্টার (Serif Bold) ---
def to_serif_bold(text):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
    trans_table = str.maketrans(normal, bold)
    return text.translate(trans_table)

# --- হ্যাকিং লোডিং এফেক্ট ---
async def hack_loading(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(to_serif_bold("Loading."))
    for i in range(3):
        await asyncio.sleep(0.3)
        await msg.edit_text(to_serif_bold("Loading.."))
        await asyncio.sleep(0.3)
        await msg.edit_text(to_serif_bold("Loading..."))
        await asyncio.sleep(0.3)
        await msg.edit_text(to_serif_bold("Loading."))
    return msg

# --- ডেটাবেস হ্যান্ডলিং ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"approved": [], "blocked": [], "pending": [], "old_classes": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- মেইন মেনু কীবোর্ড ---
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

# --- স্টার্ট কমান্ড ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    
    # লোডিং অ্যানিমেশন
    loading_msg = await hack_loading(update, context)
    await loading_msg.delete()

    # এডমিন প্যানেল
    if user.id == ADMIN_ID:
        await update.message.reply_text(
            to_serif_bold(f"Welcome Admin {user.first_name}.\nSystem Control Panel:"),
            reply_markup=get_admin_keyboard()
        )
        return

    # ব্লকড ইউজার
    if user.id in data["blocked"]:
        await update.message.reply_text(to_serif_bold("You are blocked from this system."))
        return

    # অ্যাপ্রুভড ইউজার
    if user.id in data["approved"]:
        welcome_text = (
            "𝐓𝐡𝐚𝐧𝐤𝐬 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐭𝐡𝐞 𝐛𝐨𝐭.\n"
            "𝐒𝐢𝐧𝐜𝐞 𝐲𝐨𝐮 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭, 𝐢𝐭 𝐦𝐞𝐚𝐧𝐬 𝐲𝐨𝐮 𝐚𝐫𝐞 𝐚 𝐂𝐒𝐈𝐓 𝐜𝐫𝐞𝐰.\n"
            "𝐘𝐨𝐮 𝐰𝐢𝐥𝐥 𝐠𝐞𝐭 𝐲𝐨𝐮𝐫 𝐜𝐥𝐚𝐬𝐬 𝐚𝐧𝐝 𝐧𝐞𝐜𝐞𝐬𝐬𝐚𝐫𝐲 𝐦𝐚𝐭𝐞𝐫𝐢𝐚𝐥𝐬 𝐡𝐞𝐫𝐞."
        )
        await update.message.reply_text(to_serif_bold(welcome_text), reply_markup=get_user_keyboard())
    else:
        # নতুন ইউজার
        denied_text = (
            "𝐘𝐨𝐮 𝐝𝐨 𝐧𝐨𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐛𝐨𝐭.\n"
            "𝐂𝐥𝐢𝐜𝐤 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐫𝐞𝐪𝐮𝐞𝐬𝐭 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐟𝐫𝐨𝐦 𝐀𝐝𝐦𝐢𝐧𝐬."
        )
        keyboard = [[InlineKeyboardButton(to_serif_bold("Request Access"), callback_data="request_access")]]
        await update.message.reply_text(to_serif_bold(denied_text), reply_markup=InlineKeyboardMarkup(keyboard))

# --- বাটন হ্যান্ডলার ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = load_data()
    await query.answer()

    # --- ইউজার সাইড ---
    if query.data == "request_access":
        if user.id in data["pending"]:
            await query.edit_message_text(to_serif_bold("Request already pending."))
            return
        data["pending"].append(user.id)
        save_data(data)
        await query.edit_message_text(to_serif_bold("Request sent to Admins."))
        
        # এডমিনকে নোটিফাই করা
        admin_text = f"⚠️ 𝐍𝐞𝐰 𝐑𝐞𝐪𝐮𝐞𝐬𝐭:\nName: {user.first_name}\nID: {user.id}"
        keyboard = [[InlineKeyboardButton("Approve", callback_data=f"approve_{user.id}"),
                     InlineKeyboardButton("Decline", callback_data=f"decline_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=to_serif_bold(admin_text), reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "user_support":
        await context.bot.send_message(chat_id=user.id, text=to_serif_bold("Type your message for Admin:"))
        context.user_data['state'] = 'support_mode'

    elif query.data == "user_old_class":
        if not data["old_classes"]:
            await context.bot.send_message(chat_id=user.id, text=to_serif_bold("No old classes found."))
            return
        await context.bot.send_message(chat_id=user.id, text=to_serif_bold("Sending Old Classes..."))
        for item in data["old_classes"]:
            try:
                # কপি মেসেজ ফাংশন ব্যবহার করে পুরনো ক্লাস পাঠানো
                await context.bot.copy_message(chat_id=user.id, from_chat_id=ADMIN_ID, message_id=item)
            except:
                continue

    # --- এডমিন অ্যাকশন (রিকোয়েস্ট) ---
    elif query.data.startswith("approve_"):
        target_id = int(query.data.split("_")[1])
        if target_id not in data["approved"]:
            data["approved"].append(target_id)
            if target_id in data["pending"]: data["pending"].remove(target_id)
            save_data(data)
            await context.bot.send_message(chat_id=target_id, text=to_serif_bold("Approved! Type /start."), reply_markup=get_user_keyboard())
            await query.edit_message_text(to_serif_bold(f"User {target_id} Approved."))
        else:
            await query.edit_message_text(to_serif_bold("Already Approved."))

    elif query.data.startswith("decline_"):
        target_id = int(query.data.split("_")[1])
        if target_id in data["pending"]: data["pending"].remove(target_id)
        data["blocked"].append(target_id)
        save_data(data)
        await context.bot.send_message(chat_id=target_id, text=to_serif_bold("Request Declined."))
        await query.edit_message_text(to_serif_bold(f"User {target_id} Declined."))

    # --- এডমিন প্যানেল কন্ট্রোল ---
    elif query.data == "admin_view":
        user_list = "\n".join([str(uid) for uid in data["approved"]]) if data["approved"] else "None"
        await context.bot.send_message(chat_id=ADMIN_ID, text=to_serif_bold(f"Approved Users:\n{user_list}"))

    elif query.data == "admin_add":
        await context.bot.send_message(chat_id=ADMIN_ID, text=to_serif_bold("Send User ID to ADD:"))
        context.user_data['state'] = 'add_user'

    elif query.data == "admin_remove":
        await context.bot.send_message(chat_id=ADMIN_ID, text=to_serif_bold("Send User ID to REMOVE:"))
        context.user_data['state'] = 'remove_user'
    
    elif query.data == "admin_clear_class":
        data["old_classes"] = []
        save_data(data)
        await context.bot.send_message(chat_id=ADMIN_ID, text=to_serif_bold("Old Class history cleared."))

    # --- ক্লাস সেভ করা ---
    elif query.data.startswith("save_class_"):
        msg_id = int(query.data.split("_")[2])
        if msg_id not in data["old_classes"]:
            data["old_classes"].append(msg_id)
            save_data(data)
            await query.edit_message_text(to_serif_bold("Saved to Old Class."))
        else:
            await query.edit_message_text(to_serif_bold("Already Saved."))

# --- মেসেজ হ্যান্ডলার ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    state = context.user_data.get('state')

    # --- এডমিন লজিক ---
    if user.id == ADMIN_ID:
        # যদি এডমিন কাউকে অ্যাড/রিমুভ করতে আইডি পাঠায়
        if state == 'add_user':
            try:
                new_id = int(update.message.text)
                if new_id not in data["approved"]:
                    data["approved"].append(new_id)
                    save_data(data)
                    await update.message.reply_text(to_serif_bold(f"User {new_id} Added."))
                else:
                    await update.message.reply_text(to_serif_bold("User already exists."))
            except:
                await update.message.reply_text(to_serif_bold("Invalid ID."))
            context.user_data['state'] = None
            return

        if state == 'remove_user':
            try:
                rem_id = int(update.message.text)
                if rem_id in data["approved"]:
                    data["approved"].remove(rem_id)
                    save_data(data)
                    await update.message.reply_text(to_serif_bold(f"User {rem_id} Removed."))
                else:
                    await update.message.reply_text(to_serif_bold("User not found."))
            except:
                await update.message.reply_text(to_serif_bold("Invalid ID."))
            context.user_data['state'] = None
            return

        # ব্রডকাস্ট (এডমিন যা পাঠাবে তা সব ইউজারের কাছে যাবে)
        count = 0
        for uid in data["approved"]:
            try:
                await update.message.copy(chat_id=uid)
                count += 1
            except:
                pass
        
        # ব্রডকাস্ট হওয়ার পর এডমিনকে জিজ্ঞেস করবে এটা Old Class এ সেভ করবে কি না
        save_btn = [[InlineKeyboardButton(to_serif_bold("Yes, Save to Old Class"), callback_data=f"save_class_{update.message.message_id}")]]
        await update.message.reply_text(
            to_serif_bold(f"Broadcast sent to {count} users.\nSave this to Old Class?"),
            reply_markup=InlineKeyboardMarkup(save_btn)
        )
        return

    # --- ইউজার লজিক ---
    if state == 'support_mode':
        await update.message.forward(chat_id=ADMIN_ID)
        await update.message.reply_text(to_serif_bold("Sent to Admin."))
        context.user_data['state'] = None
        return

    # সাধারণ মেসেজ
    if user.id not in data["approved"]:
         await update.message.reply_text(to_serif_bold("Access Denied. Please /start."))

# --- মেইন রানার ---
if __name__ == '__main__':
    # ডাটা ফাইল চেক
    if not os.path.exists(DATA_FILE):
        save_data({"approved": [], "blocked": [], "pending": [], "old_classes": []})

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
