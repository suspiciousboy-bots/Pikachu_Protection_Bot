#!/usr/bin/env python3
"""
⚡ PIKACHU X PROTECTION BOT - ULTIMATE GROUP MANAGEMENT ⚡
"""

import os
import sys
import asyncio
import logging
import threading
import re
from datetime import datetime, timedelta
from flask import Flask

# ────═◈═─ FLASK WEB SERVER ─═◈═────
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "⚡ Pikachu Protection Bot is running!"

@flask_app.route('/health')
def health():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port, debug=False)

threading.Thread(target=run_web, daemon=True).start()
print("🌐 Web server started")
# ──────────────────────────────────────────────────

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import Config
from database import db

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def premium_print(message, symbol="⚡"):
    border = "═" * 50
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"""
╔{border}╗
║  {symbol} [{timestamp}] {message}
╚{border}╝
""")

def get_owner_credit():
    return f"\n\n👑 Pᴏᴡᴇʀᴇᴅ Bʏ: {Config.OWNER_NAME}"

def format_mention(user):
    if user.username:
        return f"@{user.username}"
    return f"[{user.first_name}](tg://user?id={user.id})"

# ==================== MAIN MENU (UPDATED - REMOVED STAFF, SG, HISTORY) ====================
def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📊 Sᴛᴀᴛs", callback_data="stats"),
            InlineKeyboardButton("⚙️ Sᴇᴛᴛɪɴɢs", callback_data="settings")
        ],
        [
            InlineKeyboardButton("📖 Hᴇʟᴘ", callback_data="help"),
            InlineKeyboardButton("ℹ️ Aʙᴏᴜᴛ", callback_data="about")
        ],
        [
            InlineKeyboardButton("👑 Rᴏʟᴇs", callback_data="roles")
        ],
        [
            InlineKeyboardButton("➕ Aᴅᴅ Mᴇ", url=f"https://t.me/{Config.BOT_USERNAME[1:]}?startgroup=true"),
            InlineKeyboardButton("📢 Fᴏʀ Uᴘᴅᴀᴛᴇs", url=Config.UPDATES_CHANNEL)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def settings_menu():
    keyboard = [
        [
            InlineKeyboardButton("👋 Wᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"),
            InlineKeyboardButton("👋 Gᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")
        ],
        [
            InlineKeyboardButton("🛡️ Aɴᴛɪ-Sᴘᴀᴍ", callback_data="set_antispam"),
            InlineKeyboardButton("🔗 Aɴᴛɪ-Lɪɴᴋ", callback_data="set_antilink")
        ],
        [
            InlineKeyboardButton("🔞 Aɴᴛɪ-18+", callback_data="set_anti18")
        ],
        [
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def role_menu():
    keyboard = [
        [InlineKeyboardButton("👑 Fᴏᴜɴᴅᴇʀ", callback_data="role_founder")],
        [InlineKeyboardButton("⚜️ Cᴏ-Fᴏᴜɴᴅᴇʀ", callback_data="role_cofounder")],
        [InlineKeyboardButton("👔 Aᴅᴍɪɴ", callback_data="role_admin")],
        [InlineKeyboardButton("👷 Mᴏᴅᴇʀᴀᴛᴏʀ", callback_data="role_moderator")],
        [InlineKeyboardButton("🙊 Mᴜᴛᴇʀ", callback_data="role_muter")],
        [InlineKeyboardButton("🧹 Cʟᴇᴀɴᴇʀ", callback_data="role_cleaner")],
        [InlineKeyboardButton("⛑ Hᴇʟᴘᴇʀ", callback_data="role_helper")],
        [InlineKeyboardButton("🔓 Fʀᴇᴇ", callback_data="role_free")],
        [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]])

# ==================== HELPER FUNCTION ====================
async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get target user using 3 methods: reply, username, ID"""
    target = None
    reason = "No reason provided"
    
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        if context.args:
            reason = " ".join(context.args)
        return target, reason
    
    if context.args:
        first_arg = context.args[0].replace('@', '')
        try:
            if first_arg.isdigit():
                target = await context.bot.get_chat(int(first_arg))
            if not target:
                target = await context.bot.get_chat(first_arg)
        except:
            pass
        
        if len(context.args) > 1:
            reason = " ".join(context.args[1:])
    
    return target, reason

# ==================== MAIN MENU WITH IMAGE ====================
async def send_main_menu(update, context, query=None):
    """Send main menu with start image - EDITS existing message if query provided"""
    caption = f"""
✧.* ೃ⁀➷ Wᴇʟᴄᴏᴍᴇ Tᴏ Pɪᴋᴀᴄʜᴜ Pʀᴏᴛᴇᴄᴛɪᴏɴ ೃ⁀➷ ✧.*

⋆·˚ ༘ * Yᴏᴜʀ Uʟᴛɪᴍᴀᴛᴇ Gʀᴏᴜᴘ Sᴇᴄᴜʀɪᴛʏ Bᴏᴛ * ༘ ·˚⋆

❍ Bᴏᴛ: {Config.BOT_NAME}
❍ Oᴡɴᴇʀ: {Config.OWNER_NAME}

╭─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╮
                                          
   ✧.*  Fᴇᴀᴛᴜʀᴇs Aᴠᴀɪʟᴀʙʟᴇ  ✧.*          
   ❍ 50+ Lᴏᴄᴋ/Uɴʟᴏᴄᴋ Tʏᴘᴇs               
   ❍ Aᴅᴠᴀɴᴄᴇᴅ Aᴅᴍɪɴ Tᴏᴏʟs                
   ❍ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ Sʏsᴛᴇᴍ              
   ❍ Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ                    
   ❍ Rᴏʟᴇ Mᴀɴᴀɢᴇᴍᴇɴᴛ                     
   ❍ Aɴᴛɪ-Sᴘᴀᴍ Pʀᴏᴛᴇᴄᴛɪᴏɴ                
                                          
╰─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╯

📢 Fᴏʀ Uᴘᴅᴀᴛᴇs: {Config.UPDATES_CHANNEL}
💬 Sᴜᴘᴘᴏʀᴛ: {Config.SUPPORT_GROUP}

ˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    
    reply_markup = main_menu()
    
    try:
        if query:
            try:
                await query.message.edit_caption(
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Edit caption failed: {e}")
                try:
                    await query.message.edit_text(
                        caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
                except:
                    await query.message.reply_photo(
                        photo=Config.START_IMAGE,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup
                    )
        else:
            await update.message.reply_photo(
                photo=Config.START_IMAGE,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Error sending main menu: {e}")
        if query:
            await query.message.edit_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

# ==================== START COMMAND ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    
    caption = f"""
✧.* ೃ⁀➷ Wᴇʟᴄᴏᴍᴇ Tᴏ Pɪᴋᴀᴄʜᴜ Pʀᴏᴛᴇᴄᴛɪᴏɴ ೃ⁀➷ ✧.*

⋆·˚ ༘ * Yᴏᴜʀ Uʟᴛɪᴍᴀᴛᴇ Gʀᴏᴜᴘ Sᴇᴄᴜʀɪᴛʏ Bᴏᴛ * ༘ ·˚⋆

❍ Bᴏᴛ: {Config.BOT_NAME}
❍ Oᴡɴᴇʀ: {Config.OWNER_NAME}

╭─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╮
                                          
   ✧.*  Fᴇᴀᴛᴜʀᴇs Aᴠᴀɪʟᴀʙʟᴇ  ✧.*          
   ❍ 50+ Lᴏᴄᴋ/Uɴʟᴏᴄᴋ Tʏᴘᴇs               
   ❍ Aᴅᴠᴀɴᴄᴇᴅ Aᴅᴍɪɴ Tᴏᴏʟs                
   ❍ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ Sʏsᴛᴇᴍ              
   ❍ Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ                    
   ❍ Rᴏʟᴇ Mᴀɴᴀɢᴇᴍᴇɴᴛ                     
   ❍ Aɴᴛɪ-Sᴘᴀᴍ Pʀᴏᴛᴇᴄᴛɪᴏɴ                
                                          
╰─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╯

📢 Fᴏʀ Uᴘᴅᴀᴛᴇs: {Config.UPDATES_CHANNEL}
💬 Sᴜᴘᴘᴏʀᴛ: {Config.SUPPORT_GROUP}

ˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    
    try:
        await update.message.reply_photo(
            photo=Config.START_IMAGE,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu()
        )
    except Exception as e:
        logger.error(f"Image send failed: {e}")
        await update.message.reply_text(
            caption,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu()
        )

# ==================== HELP COMMAND ====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 Powerfull Commands List 📖

═══════════════════════════

👑 Admin Commands:

/warn @user - Warn user
/unwarn @user - Remove warns
/warns @user - Check warns
/resetwarns @user - Reset warns
/mute @user - Mute user
/unmute @user - Unmute user
/kick @user - Kick user
/ban @user - Ban user
/unban @user - Unban user
/approve @user - Approve user
/unapprove @user - Remove approval
/reload - Reload admins
/settings - Change settings

/promote @user - Make user admin
/demote @user - Remove admin rights

👥 Role Commands:

/cofounder @user - Add Co-Founder
/uncofounder @user - Remove Co-Founder
/mod @user - Add Moderator
/unmod @user - Remove Moderator
/muter @user - Add Muter
/unmuter @user - Remove Muter
/cleaner @user - Add Cleaner
/uncleaner @user - Remove Cleaner
/helper @user - Add Helper
/unhelper @user - Remove Helper
/free @user - Add Free User
/unfree @user - Remove Free User
/roles - View all roles

📌 Pin Commands:

/pin - Pin a message
/unpin - Unpin message
/pinned - View pinned
/editpin - Edit pin
/delpin - Delete pin

🗑️ Delete Commands:

/del - Delete message
/logdel - Delete & log
/purge - Delete multiple

🔒 Lock/Unlock Commands:

/locktypes - Show lock types
/lock <type> - Lock message type
/unlock <type> - Unlock message type

📊 General Commands:

/start - Start bot
/help - Get help
/about - About bot
/ping - Bot status
/staff - View staff
/info - User info
/infopvt - Private info
/me - Your info
/geturl - Get message link
/sg @user - Show user's dark past (name/username history)
/history @user - Full history (name/username changes)
/chat - Chat with bot

👋 Welcome & Goodbye:

/enablewelcome - Enable welcome
/disablewelcome - Disable welcome
/enablegoodbye - Enable goodbye
/disablegoodbye - Disable goodbye

🔰 Filter Commands:

/filter - Add filter
/stopfilter - Remove filter
/filters - List filters

═══════════════════════════

🔥 Powered By ── ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ──
"""
    await update.message.reply_text(text, parse_mode=None, reply_markup=back_button())

# ==================== ABOUT COMMAND ====================
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
⚡ About {Config.BOT_NAME} ⚡

────═◈═─ ✧◈✧ ─═◈═────
🤖 Name: {Config.BOT_NAME}  
📌 Username: {Config.BOT_USERNAME} 
👑 Owner: {Config.OWNER_NAME} 
📞 Contact: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 Description:
The Ultimate Group Management Bot

🔰 Status: Active

📢 For Updates: {Config.UPDATES_CHANNEL}
💬 Support: {Config.SUPPORT_GROUP}

{get_owner_credit()}
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())

# ==================== PING COMMAND ====================
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = datetime.now()
    msg = await update.message.reply_text("✦ ˚₊· ͟͟͞͞➳❥ Pinging...")
    end_time = datetime.now()
    ping_time = (end_time - start_time).microseconds / 1000
    
    text = f"""
✧.* ೃ⁀➷ Bot Status ೃ⁀➷ ✧.*

˚₊· ➳❥ Status : ✅ Online
˚₊· ➳❥ Ping : {ping_time:.2f}ms
˚₊· ➳❥ Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

﹌﹌﹌ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ﹌﹌﹌
"""
    await msg.edit_text(text, parse_mode=ParseMode.HTML)

# ==================== STAFF COMMAND ====================
async def staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    chat = update.effective_chat
    chat_id = chat.id
    
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        
        owner = None
        admin_list = []
        
        for admin in admins:
            if admin.status == 'creator':
                owner = admin.user
            else:
                admin_list.append(admin.user)
        
        staff_members = db.get_all_roles(chat_id)
        custom_roles = {}
        for member in staff_members:
            user_id = member.get('user_id')
            role = member.get('role', 'Member')
            if user_id:
                custom_roles[user_id] = role
        
        text = f"""✧.* ೃ⁀➷ Sᴛᴀғғ Lɪsᴛ ೃ⁀➷ ✧.*

────═◈═─ ✧◈✧ ─═◈═────
"""
        
        def get_mention(user):
            if user.username:
                return f"@{user.username}"
            return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        
        if owner:
            owner_role = custom_roles.get(owner.id, 'Fᴏᴜɴᴅᴇʀ')
            text += f"\n👑 {owner_role}\n"
            text += f"╰┈➤ {get_mention(owner)}\n"
        
        if admin_list:
            text += f"\n👔 Aᴅᴍɪɴs ({len(admin_list)})\n"
            for admin in admin_list:
                role = custom_roles.get(admin.id, 'Aᴅᴍɪɴ')
                text += f"╰┈➤ {get_mention(admin)}\n"
        
        role_groups = {
            'cofounder': ('⚜️', 'Cᴏ-Fᴏᴜɴᴅᴇʀs'),
            'mod': ('👷', 'Mᴏᴅᴇʀᴀᴛᴏʀs'),
            'muter': ('🙊', 'Mᴜᴛᴇʀs'),
            'cleaner': ('🧹', 'Cʟᴇᴀɴᴇʀs'),
            'helper': ('⛑', 'Hᴇʟᴘᴇʀs'),
            'free': ('🔓', 'Fʀᴇᴇ Usᴇʀs')
        }
        
        for role_key, (emoji, title) in role_groups.items():
            members = [m for m in staff_members if m.get('role') == role_key]
            if members:
                text += f"\n{emoji} {title} ({len(members)})\n"
                for member in members:
                    try:
                        user = await context.bot.get_chat(member.get('user_id'))
                        text += f"╰┈➤ {get_mention(user)}\n"
                    except:
                        text += f"╰┈➤ Uɴᴋɴᴏᴡɴ\n"
        
        text += f"\n\n{get_owner_credit()}"
        text += "\n\nˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        
    except Exception as e:
        await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")

# ==================== INFO COMMANDS ====================

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        target = update.effective_user
    
    role = db.get_user_role(target.id, update.effective_chat.id)
    stats = db.get_user_stats(target.id)
    
    text = f"""
✧.* ೃ⁀➷ User Information ೃ⁀➷ ✧.*

❍ Name : {format_mention(target)}
❍ Username : @{target.username or 'None'}
❍ ID : {target.id}
❍ Role : {role.upper()}
❍ Messages : {stats.get('messages', 0)}
❍ Groups : {stats.get('groups', 0)}
❍ Warns : {stats.get('warns', 0)}

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def infopvt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    text = f"""
✧.* ೃ⁀➷ Your Information ೃ⁀➷ ✧.*

❍ Name : {user.first_name} {user.last_name or ''}
❍ Username : @{user.username or 'None'}
❍ ID : {user.id}
❍ First Name : {user.first_name or 'None'}
❍ Last Name : {user.last_name or 'None'}
❍ Language : {user.language_code or 'Unknown'}
❍ Is Bot : {user.is_bot}

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    text = f"""
✧.* ೃ⁀➷ Your Profile ೃ⁀➷ ✧.*

❍ Name : {user.first_name} {user.last_name or ''}
❍ Username : @{user.username or 'None'}
❍ ID : {user.id}
❍ First Name : {user.first_name or 'None'}
❍ Last Name : {user.last_name or 'None'}

You are viewing your own profile

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def geturl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a message!")
        return
    
    msg = update.message.reply_to_message
    chat_id = update.effective_chat.id
    msg_id = msg.message_id
    
    url = f"https://t.me/c/{str(chat_id)[4:]}/{msg_id}"
    
    text = f"""
✧.* ೃ⁀➷ Message Link ೃ⁀➷ ✧.*

Link: <a href='{url}'>Click Here</a>

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💬 Send me a message to chat!\nUsage: /chat <text>")
        return
    
    text = " ".join(context.args)
    await update.message.reply_text(f"💬 You said: {text}\n\n{get_owner_credit()}")

# ==================== LOCKTYPES COMMAND ====================
async def locktypes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
✧.* ೃ⁀➷ Lock Types ೃ⁀➷ ✧.*

Available Lock Types:

all - Lock all types
text - Text messages
photo - Photos
video - Videos
audio - Audio files
gif - GIFs
sticker - Stickers
poll - Polls
game - Games
link - Links
forward - Forwarded messages
contact - Contacts
location - Locations
document - Documents
voice - Voice messages
video_note - Video notes
reply - Replies
mention - Mentions
hashtag - Hashtags
bot - Bot messages
inline - Inline queries

Usage:
/lock text - Lock text messages
/unlock text - Unlock text messages

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ==================== LOCK COMMAND ====================
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /lock <type>\nUse /locktypes to see all types")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can lock!")
            return
    except:
        return
    
    lock_type = context.args[0].lower()
    
    settings = db.get_settings(chat.id)
    locked = settings.get('locked_types', [])
    if lock_type not in locked:
        locked.append(lock_type)
    db.update_settings(chat.id, 'locked_types', locked)
    
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Locked ೃ⁀➷ ✧.*

✅ {lock_type} messages are now LOCKED!

Users cannot send {lock_type} messages
Admins can still send

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

# ==================== UNLOCK COMMAND ====================
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not context.args:
        await update.message.reply_text("❌ Usage: /unlock <type>")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can unlock!")
            return
    except:
        return
    
    lock_type = context.args[0].lower()
    
    settings = db.get_settings(chat.id)
    locked = settings.get('locked_types', [])
    if lock_type in locked:
        locked.remove(lock_type)
    db.update_settings(chat.id, 'locked_types', locked)
    
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Unlocked ೃ⁀➷ ✧.*

✅ {lock_type} messages are now UNLOCKED!

Users can now send {lock_type} messages

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

# ==================== WARN COMMANDS ====================
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can warn!")
            return
    except:
        return
    
    target, reason = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /warn @username reason\n"
            "2. /warn 123456789 reason\n"
            "3. Reply to user: /warn reason"
        )
        return
    
    if target.is_bot:
        await update.message.reply_text("❌ Can't warn bots!")
        return
    
    db.add_warning(target.id, chat.id, reason, user.id)
    warn_count = db.get_warning_count(target.id, chat.id)
    settings = db.get_settings(chat.id)
    max_warns = settings.get('warn_limit', Config.MAX_WARNINGS)
    
    text = f"""
⚠️ Warning! ⚠️

User: {format_mention(target)}
Warn: {warn_count}/{max_warns}
Reason: {reason}
"""
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    if warn_count >= max_warns:
        await update.message.reply_text(f"⚠️ {target.first_name} has reached the warn limit!", parse_mode=ParseMode.HTML)

async def unwarn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can unwarn!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /unwarn @username\n"
            "2. /unwarn 123456789\n"
            "3. Reply to user: /unwarn"
        )
        return
    
    db.clear_warnings(target.id, chat.id)
    await update.message.reply_text(f"✅ Cleared all warnings for {target.first_name}!", parse_mode=ParseMode.HTML)

async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    chat = update.effective_chat
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        target = update.effective_user
    
    warnings = db.get_warnings(target.id, chat.id)
    
    if not warnings:
        await update.message.reply_text(f"✅ {target.first_name} has no warnings!", parse_mode=ParseMode.HTML)
        return
    
    text = f"⚠️ Warnings for {target.first_name}:\n\n"
    for i, warn in enumerate(warnings, 1):
        text += f"└ {i}. {warn['reason']}\n"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def resetwarns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can reset warns!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /resetwarns @username\n"
            "2. /resetwarns 123456789\n"
            "3. Reply to user: /resetwarns"
        )
        return
    
    db.clear_warnings(target.id, chat.id)
    await update.message.reply_text(f"✅ Cleared all warnings for {target.first_name}!", parse_mode=ParseMode.HTML)

# ==================== MUTE COMMAND ====================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can mute!")
            return
    except:
        return
    
    target, reason = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /mute @username 60 reason\n"
            "2. /mute 123456789 60 reason\n"
            "3. Reply to user: /mute 60 reason"
        )
        return
    
    if target.is_bot:
        await update.message.reply_text("❌ Can't mute bots!")
        return
    
    duration = Config.MUTE_DURATION
    if context.args:
        for arg in context.args:
            if arg.isdigit():
                duration = int(arg)
                break
    
    db.add_mute(target.id, chat.id, duration, reason, user.id)
    
    try:
        await context.bot.restrict_chat_member(
            chat.id,
            target.id,
            ChatPermissions(can_send_messages=False)
        )
    except:
        pass
    
    text = f"""
🔇 Muted! 🔇

User: {target.first_name}
Duration: {duration}s
Reason: {reason}
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can unmute!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /unmute @username\n"
            "2. /unmute 123456789\n"
            "3. Reply to user: /unmute"
        )
        return
    
    db.remove_mute(target.id, chat.id)
    
    try:
        await context.bot.restrict_chat_member(
            chat.id,
            target.id,
            ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
    except:
        pass
    
    await update.message.reply_text(f"🔊 Unmuted {target.first_name}!", parse_mode=ParseMode.HTML)

# ==================== KICK COMMAND ====================
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can kick!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /kick @username\n"
            "2. /kick 123456789\n"
            "3. Reply to user: /kick"
        )
        return
    
    if target.is_bot:
        await update.message.reply_text("❌ Can't kick bots!")
        return
    
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await context.bot.unban_chat_member(chat.id, target.id)
        await update.message.reply_text(f"👢 Kicked {target.first_name}!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==================== BAN COMMAND ====================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can ban!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /ban @username reason\n"
            "2. /ban 123456789 reason\n"
            "3. Reply to user: /ban reason"
        )
        return
    
    if target.is_bot:
        await update.message.reply_text("❌ Can't ban bots!")
        return
    
    try:
        await context.bot.ban_chat_member(chat.id, target.id)
        await update.message.reply_text(f"🚫 Banned {target.first_name}!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can unban!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /unban @username\n"
            "2. /unban 123456789\n"
            "3. Reply to user: /unban"
        )
        return
    
    try:
        await context.bot.unban_chat_member(chat.id, target.id)
        await update.message.reply_text(f"✅ Unbanned {target.first_name}!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==================== APPROVE COMMAND ====================
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can approve!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /approve @username\n"
            "2. /approve 123456789\n"
            "3. Reply to user: /approve"
        )
        return
    
    db.approve_user(target.id, chat.id)
    await update.message.reply_text(f"✅ Approved {target.first_name}!", parse_mode=ParseMode.HTML)

async def unapprove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can unapprove!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /unapprove @username\n"
            "2. /unapprove 123456789\n"
            "3. Reply to user: /unapprove"
        )
        return
    
    db.unapprove_user(target.id, chat.id)
    await update.message.reply_text(f"❌ Unapproved {target.first_name}!", parse_mode=ParseMode.HTML)

# ==================== RELOAD COMMAND ====================
async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can reload!")
            return
    except:
        return
    
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Reloaded ೃ⁀➷ ✧.*

✅ Admin list has been reloaded!

All admins have been updated
New staff changes applied

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

# ==================== SETTINGS COMMAND ====================
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can view settings!")
            return
    except:
        return
    
    settings_data = db.get_settings(chat.id)
    
    text = f"""
✧.* ೃ⁀➷ Group Settings ೃ⁀➷ ✧.*

Current Settings:

Welcome: {'✅ Enabled' if settings_data.get('welcome', True) else '❌ Disabled'}
Goodbye: {'✅ Enabled' if settings_data.get('goodbye', True) else '❌ Disabled'}
Anti-Spam: {'✅ Enabled' if settings_data.get('antispam', True) else '❌ Disabled'}
Anti-Link: {'✅ Enabled' if settings_data.get('antilink', False) else '❌ Disabled'}
Anti-18+: {'✅ Enabled' if settings_data.get('anti18', True) else '❌ Disabled'}
Warn Limit: {settings_data.get('warn_limit', 3)}

Commands:
/enablewelcome - Enable welcome
/disablewelcome - Disable welcome
/enablegoodbye - Enable goodbye
/disablegoodbye - Disable goodbye
/lock <type> - Lock message type
/unlock <type> - Unlock message type
/filter - Add filter
/stopfilter - Remove filter
/reload - Reload admins

{get_owner_credit()}
ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=settings_menu())

# ==================== ROLE COMMANDS ====================
async def add_role(update: Update, context: ContextTypes.DEFAULT_TYPE, role_name):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text(f"❌ Only admins can add roles!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            f"⚠️ Usage:\n"
            f"1. /{role_name} @username\n"
            f"2. /{role_name} 123456789\n"
            f"3. Reply to user: /{role_name}"
        )
        return
    
    db.set_user_role(target.id, chat.id, role_name)
    await update.message.reply_text(f"✅ Added {role_name.upper()} role to {target.first_name}!", parse_mode=ParseMode.HTML)

async def remove_role(update: Update, context: ContextTypes.DEFAULT_TYPE, role_name):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text(f"❌ Only admins can remove roles!")
            return
    except:
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            f"⚠️ Usage:\n"
            f"1. /un{role_name} @username\n"
            f"2. /un{role_name} 123456789\n"
            f"3. Reply to user: /un{role_name}"
        )
        return
    
    db.remove_user_role(target.id, chat.id)
    await update.message.reply_text(f"❌ Removed {role_name.upper()} role from {target.first_name}!", parse_mode=ParseMode.HTML)

async def roles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    chat_id = update.effective_chat.id
    staff_members = db.get_all_roles(chat_id)
    
    if not staff_members:
        await update.message.reply_text("❌ No roles found in this group!")
        return
    
    text = f"""
✧.* ೃ⁀➷ Roles List ೃ⁀➷ ✧.*

────═◈═─ ✧◈✧ ─═◈═────
"""
    
    role_groups = {
        'cofounder': ('⚜️', 'Co-Founders'),
        'mod': ('👷', 'Moderators'),
        'muter': ('🙊', 'Mutters'),
        'cleaner': ('🧹', 'Cleaners'),
        'helper': ('⛑', 'Helpers'),
        'free': ('🔓', 'Free Users')
    }
    
    for role_key, (emoji, title) in role_groups.items():
        members = [m for m in staff_members if m.get('role') == role_key]
        if members:
            text += f"\n{emoji} {title} ({len(members)})\n"
            for member in members:
                try:
                    user = await context.bot.get_chat(member.get('user_id'))
                    text += f"╰┈➤ {user.first_name} (ID: {user.id})\n"
                except:
                    text += f"╰┈➤ Unknown (ID: {member.get('user_id')})\n"
    
    text += f"\n{get_owner_credit()}"
    text += "\n\nˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=role_menu())

# ==================== PIN COMMANDS ====================
async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a message to pin!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can pin!")
            return
    except:
        return
    
    try:
        await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
        await update.message.reply_text("📌 Message pinned!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can unpin!")
            return
    except:
        return
    
    try:
        await context.bot.unpin_chat_message(chat.id)
        await update.message.reply_text("📌 Message unpinned!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def pinned(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    chat = update.effective_chat
    
    try:
        pinned_msg = await context.bot.get_chat(chat.id)
        if pinned_msg.pinned_message:
            text = f"""
📌 Current Pinned Message

Text:
{pinned_msg.pinned_message.text or 'No text'}

Link: <a href='https://t.me/c/{str(chat.id)[4:]}/{pinned_msg.pinned_message.message_id}'>Click Here</a>
"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ No pinned message in this group!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def editpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a message to edit pin!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can edit pin!")
            return
    except:
        return
    
    try:
        await context.bot.unpin_chat_message(chat.id)
        await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
        await update.message.reply_text("📌 Pin edited!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def delpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can delete pin!")
            return
    except:
        return
    
    try:
        await context.bot.unpin_chat_message(chat.id)
        await update.message.reply_text("🗑️ Pin deleted!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==================== DELETE COMMANDS ====================
async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a message to delete!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can delete!")
            return
    except:
        return
    
    try:
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await context.bot.delete_message(chat.id, update.message.message_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def logdel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a message to delete & log!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use this!")
            return
    except:
        return
    
    msg = update.message.reply_to_message
    text = msg.text or "No text"
    sender = msg.from_user
    
    log_text = f"""
🗑️ Log Delete

❍ User: {format_mention(sender)}
❍ Text: {text}
❍ Admin: {format_mention(user)}
❍ Group: {chat.title}
"""
    
    try:
        await context.bot.send_message(Config.LOG_CHANNEL, log_text, parse_mode=ParseMode.HTML)
    except:
        pass
    
    try:
        await context.bot.delete_message(chat.id, msg.message_id)
        await context.bot.delete_message(chat.id, update.message.message_id)
        await update.message.reply_text("✅ Message deleted & logged!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to the starting message!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can purge!")
            return
    except:
        return
    
    start_msg = update.message.reply_to_message.message_id
    current_msg = update.message.message_id
    
    try:
        for msg_id in range(start_msg, current_msg):
            try:
                await context.bot.delete_message(chat.id, msg_id)
            except:
                pass
        await update.message.reply_text("🧹 Messages purged!", parse_mode=ParseMode.HTML)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==================== SG / HISTORY COMMANDS (UPDATED WITH FETCHING MESSAGE) ====================
async def sg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target, _ = await get_target_user(update, context)
    
    if not target:
        target = update.effective_user
    
    # Send "Fetching..." message
    fetching_msg = await update.message.reply_text(
        f"📜 Fᴇᴛᴄʜɪɴɢ ʜɪsᴛᴏʀʏ ғᴏʀ {target.first_name}...\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ʀᴇsᴘᴏɴsᴇ."
    )
    
    # Get history from database
    history = db.get_user_history(target.id)
    
    if not history:
        await fetching_msg.edit_text(
            f"❌ Nᴏ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ ғᴏʀ {target.first_name}!\n\n"
            f"💡 Hɪsᴛᴏʀʏ ɪs ᴏɴʟʏ ʀᴇᴄᴏʀᴅᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴛɪᴍᴇ I ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ."
        )
        return
    
    # Format the history like SangMata style
    name_changes = []
    username_changes = []
    
    for entry in history:
        name = f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip()
        if name:
            name_changes.append({
                'name': name,
                'timestamp': entry.get('timestamp', '')
            })
        if entry.get('username'):
            username_changes.append({
                'username': entry.get('username'),
                'timestamp': entry.get('timestamp', '')
            })
    
    text = f"""
📊 **Usᴇʀ Hɪsᴛᴏʀʏ (Dᴀʀᴋ Pᴀsᴛ)** 📊
━━━━━━━━━━━━━━━━━━━━━━━━━━
❍ Usᴇʀ: {target.first_name}
❍ ID: `{target.id}`
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    if name_changes:
        text += "📛 **Nᴀᴍᴇ Cʜᴀɴɢᴇs:**\n"
        for change in name_changes:
            ts = change['timestamp']
            if isinstance(ts, datetime):
                ts = ts.strftime("%d %b %Y, %I:%M %p")
            text += f"╰┈➤ {change['name']}  `({ts})`\n"
        text += "\n"
    else:
        text += "📛 Nᴏ ɴᴀᴍᴇ ᴄʜᴀɴɢᴇs ʀᴇᴄᴏʀᴅᴇᴅ\n\n"
    
    if username_changes:
        text += "🔰 **Usᴇʀɴᴀᴍᴇ Cʜᴀɴɢᴇs:**\n"
        for change in username_changes:
            ts = change['timestamp']
            if isinstance(ts, datetime):
                ts = ts.strftime("%d %b %Y, %I:%M %p")
            text += f"╰┈➤ @{change['username']}  `({ts})`\n"
        text += "\n"
    else:
        text += "🔰 Nᴏ ᴜsᴇʀɴᴀᴍᴇ ᴄʜᴀɴɢᴇs ʀᴇᴄᴏʀᴅᴇᴅ\n\n"
    
    text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Tᴏᴛᴀʟ Nᴀᴍᴇ Cʜᴀɴɢᴇs: {len(name_changes)}
📊 Tᴏᴛᴀʟ Usᴇʀɴᴀᴍᴇ Cʜᴀɴɢᴇs: {len(username_changes)}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Fᴇᴛᴄʜᴇᴅ ғʀᴏᴍ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ

{get_owner_credit()}
ˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    
    await fetching_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target, _ = await get_target_user(update, context)
    
    if not target:
        target = update.effective_user
    
    # Send "Fetching full history..." message
    fetching_msg = await update.message.reply_text(
        f"📜 Fᴇᴛᴄʜɪɴɢ ғᴜʟʟ ʜɪsᴛᴏʀʏ ғᴏʀ {target.first_name}...\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ʀᴇsᴘᴏɴsᴇ."
    )
    
    history = db.get_user_history(target.id)
    
    if not history:
        await fetching_msg.edit_text(
            f"❌ Nᴏ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ ғᴏʀ {target.first_name}!\n\n"
            f"💡 Hɪsᴛᴏʀʏ ɪs ᴏɴʟʏ ʀᴇᴄᴏʀᴅᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴛɪᴍᴇ I ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ."
        )
        return
    
    text = f"""
📜 **Fᴜʟʟ Hɪsᴛᴏʀʏ Oғ {target.first_name}** 📜
━━━━━━━━━━━━━━━━━━━━━━━━━━
❍ Usᴇʀ: {target.first_name}
❍ ID: `{target.id}`
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for entry in history:
        name = f"{entry.get('first_name', '')} {entry.get('last_name', '')}".strip()
        username = entry.get('username', 'Nᴏɴᴇ')
        ts = entry.get('timestamp', '')
        if isinstance(ts, datetime):
            ts = ts.strftime("%d %b %Y, %I:%M %p")
        text += f"╰┈➤ **{name}**  (@{username})  `{ts}`\n"
    
    text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Tᴏᴛᴀʟ Eɴᴛʀɪᴇs: {len(history)}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Fᴇᴛᴄʜᴇᴅ ғʀᴏᴍ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ

{get_owner_credit()}
ˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    
    await fetching_msg.edit_text(text, parse_mode=ParseMode.HTML)

# ==================== WELCOME & GOODBYE COMMANDS ====================
async def enablewelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use this!")
            return
    except:
        return
    
    db.update_settings(chat.id, 'welcome', True)
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Welcome Enabled ೃ⁀➷ ✧.*

✅ Welcome messages are now enabled!

New members will be welcomed automatically

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

async def disablewelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use this!")
            return
    except:
        return
    
    db.update_settings(chat.id, 'welcome', False)
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Welcome Disabled ೃ⁀➷ ✧.*

❌ Welcome messages are now disabled!

New members will NOT be welcomed

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

async def enablegoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use this!")
            return
    except:
        return
    
    db.update_settings(chat.id, 'goodbye', True)
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Goodbye Enabled ೃ⁀➷ ✧.*

✅ Goodbye messages are now enabled!

When a member leaves, a goodbye message will be sent

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

async def disablegoodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can use this!")
            return
    except:
        return
    
    db.update_settings(chat.id, 'goodbye', False)
    await update.message.reply_text(
        f"""✧.* ೃ⁀➷ Goodbye Disabled ೃ⁀➷ ✧.*

❌ Goodbye messages are now disabled!

When a member leaves, no goodbye message will be sent

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
        parse_mode=ParseMode.HTML
    )

# ==================== FILTER COMMANDS ====================
async def filter_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /filter <keyword> <reply>")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can add filters!")
            return
    except:
        return
    
    keyword = context.args[0].lower()
    reply_text = " ".join(context.args[1:])
    
    db.add_filter(chat.id, keyword, reply_text)
    await update.message.reply_text(f"✅ Filter added!\n\n{keyword} -> {reply_text}", parse_mode=ParseMode.HTML)

async def stopfilter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /stopfilter <keyword>")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if not member.status in ['administrator', 'creator']:
            await update.message.reply_text("❌ Only admins can remove filters!")
            return
    except:
        return
    
    keyword = context.args[0].lower()
    db.remove_filter(chat.id, keyword)
    await update.message.reply_text(f"✅ Filter removed!\n\n{keyword}", parse_mode=ParseMode.HTML)

async def filters_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        return
    
    chat = update.effective_chat
    filters_data = db.get_filters(chat.id)
    
    if not filters_data:
        await update.message.reply_text("❌ No filters found in this group!")
        return
    
    text = f"""
✧.* ೃ⁀➷ Filters List ೃ⁀➷ ✧.*

Active Filters ({len(filters_data)})
"""
    for f in filters_data:
        text += f"\n╰┈➤ {f.get('keyword')} -> {f.get('reply_text')[:50]}..."
    
    text += f"\n\n{get_owner_credit()}"
    text += "\n\nˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ"
    
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ==================== WELCOME/GREETINGS WITH PFP ====================
async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.new_chat_members:
        return
    
    chat = update.effective_chat
    settings = db.get_settings(chat.id)
    
    if not settings.get('welcome', True):
        return
    
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        
        db.add_user(member.id, member.username, member.first_name)
        db.add_user_history(member.id, {
            "first_name": member.first_name,
            "last_name": member.last_name or "",
            "username": member.username or ""
        })
        
        try:
            member_count = await context.bot.get_chat_member_count(chat.id)
        except Exception as e:
            logger.warning(f"Could not get member count: {e}")
            member_count = "?"
        
        role = db.get_user_role(member.id, chat.id) or "Member"
        
        try:
            user_full = await context.bot.get_chat(member.id)
            bio = user_full.bio or "Not set"
        except:
            bio = "Not set"
        
        try:
            photos = await context.bot.get_user_profile_photos(member.id, limit=1)
            if photos.total_count > 0:
                photo = photos.photos[0][-1].file_id
                has_dp = True
            else:
                has_dp = False
                photo = None
        except:
            has_dp = False
            photo = None
        
        welcome_msg = f"""
✧.* ೃ⁀➷ Welcome To {chat.title} ! ೃ⁀➷ ✧.*

────═◈═─ ✧◈✧ ─═◈═────

❍ Name: {member.first_name} {member.last_name or ''}
❍ ID: {member.id}
❍ Username: @{member.username or 'None'}
❍ Bio: {bio}

────═◈═─ ✧◈✧ ─═◈═────

❍ Group: {chat.title}
❍ Members: {member_count}
❍ Role: {role.upper()}

────═◈═─ ✧◈✧ ─═◈═────
Protected By {Config.BOT_NAME}

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
        
        if has_dp and photo:
            try:
                await context.bot.send_photo(
                    chat.id,
                    photo,
                    caption=welcome_msg,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Welcome photo error: {e}")
                await context.bot.send_message(chat.id, welcome_msg, parse_mode=ParseMode.HTML)
        else:
            no_dp_msg = f"""
✧.* ೃ⁀➷ Welcome To {chat.title} ! ೃ⁀➷ ✧.*

────═◈═─ ✧◈✧ ─═◈═────

No Profile Picture

❍ Name: {member.first_name} {member.last_name or ''}
❍ ID: {member.id}
❍ Username: @{member.username or 'None'}
❍ Bio: {bio}

────═◈═─ ✧◈✧ ─═◈═────

❍ Group: {chat.title}
❍ Members: {member_count}
❍ Role: {role.upper()}

────═◈═─ ✧◈✧ ─═◈═────
Protected By {Config.BOT_NAME}

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
            try:
                await context.bot.send_message(chat.id, no_dp_msg, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.error(f"Welcome text error: {e}")
                await context.bot.send_message(chat.id, no_dp_msg.replace('<', '').replace('>', ''))

async def goodbye_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.left_chat_member:
        return
    
    chat = update.effective_chat
    settings = db.get_settings(chat.id)
    
    if not settings.get('goodbye', True):
        return
    
    member = update.message.left_chat_member
    if member.is_bot:
        return
    
    try:
        member_count = await context.bot.get_chat_member_count(chat.id)
    except:
        member_count = "?"
    
    role = db.get_user_role(member.id, chat.id) or "Member"
    
    try:
        user_full = await context.bot.get_chat(member.id)
        bio = user_full.bio or "Not set"
    except:
        bio = "Not set"
    
    try:
        photos = await context.bot.get_user_profile_photos(member.id, limit=1)
        if photos.total_count > 0:
            photo = photos.photos[0][-1].file_id
            has_dp = True
        else:
            has_dp = False
            photo = None
    except:
        has_dp = False
        photo = None
    
    goodbye_msg = f"""
✧.* ೃ⁀➷ Goodbye! ೃ⁀➷ ✧.*

────═◈═─ ✧◈✧ ─═◈═────

{member.first_name} has left the {chat.title} !

❍ Name: {member.first_name} {member.last_name or ''}
❍ ID: {member.id}
❍ Username: @{member.username or 'None'}
❍ Bio: {bio}

────═◈═─ ✧◈✧ ─═◈═────

❍ Group: {chat.title}
❍ Members: {member_count}
❍ Role: {role.upper()}

────═◈═─ ✧◈✧ ─═◈═────
We will miss you!

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
    
    if has_dp and photo:
        try:
            await context.bot.send_photo(
                chat.id,
                photo,
                caption=goodbye_msg,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Goodbye photo error: {e}")
            await context.bot.send_message(chat.id, goodbye_msg, parse_mode=ParseMode.HTML)
    else:
        no_dp_msg = f"""
✧.* ೃ⁀➷ Goodbye! ೃ⁀➷ ✧.*

────═◈═─ ✧◈✧ ─═◈═────

No Profile Picture

{member.first_name} has left the {chat.title} !

❍ Name: {member.first_name} {member.last_name or ''}
❍ ID: {member.id}
❍ Username: @{member.username or 'None'}
❍ Bio: {bio}

────═◈═─ ✧◈✧ ─═◈═────

❍ Group: {chat.title}
❍ Members: {member_count}
❍ Role: {role.upper()}

────═◈═─ ✧◈✧ ─═◈═────
We will miss you!

ˏˋ°•*⁀➷ Powered By ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ
"""
        try:
            await context.bot.send_message(chat.id, no_dp_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Goodbye text error: {e}")
            await context.bot.send_message(chat.id, no_dp_msg.replace('<', '').replace('>', ''))

# ==================== PROMOTE COMMAND ====================
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status != 'creator':
            await update.message.reply_text("❌ Only group creator can promote!")
            return
    except:
        await update.message.reply_text("❌ You don't have permission!")
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /promote @username\n"
            "2. /promote 123456789\n"
            "3. Reply to user: /promote"
        )
        return
    
    if target.is_bot:
        await update.message.reply_text("❌ Can't promote bots!")
        return
    
    try:
        await context.bot.promote_chat_member(
            chat.id,
            target.id,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,
            can_manage_chat=True,
            can_manage_video_chats=True,
            is_anonymous=False
        )
        
        await update.message.reply_text(
            f"""✧.* ೃ⁀➷ Pʀᴏᴍᴏᴛᴇᴅ! ೃ⁀➷ ✧.*

✅ {target.first_name} has been promoted to Admin!

❍ They now have admin powers
❍ Can manage messages, users, and settings

ˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==================== DEMOTE COMMAND ====================
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ['group', 'supergroup']:
        await update.message.reply_text("❌ This command only works in groups!")
        return
    
    user = update.effective_user
    chat = update.effective_chat
    
    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        if member.status != 'creator':
            await update.message.reply_text("❌ Only group creator can demote!")
            return
    except:
        await update.message.reply_text("❌ You don't have permission!")
        return
    
    target, _ = await get_target_user(update, context)
    
    if not target:
        await update.message.reply_text(
            "⚠️ Usage:\n"
            "1. /demote @username\n"
            "2. /demote 123456789\n"
            "3. Reply to user: /demote"
        )
        return
    
    if target.is_bot:
        await update.message.reply_text("❌ Can't demote bots!")
        return
    
    try:
        target_member = await context.bot.get_chat_member(chat.id, target.id)
        if target_member.status == 'creator':
            await update.message.reply_text("❌ Cannot demote the group creator!")
            return
    except:
        pass
    
    try:
        await context.bot.promote_chat_member(
            chat.id,
            target.id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
            is_anonymous=False
        )
        
        await update.message.reply_text(
            f"""✧.* ೃ⁀➷ Dᴇᴍᴏᴛᴇᴅ! ೃ⁀➷ ✧.*

✅ {target.first_name} has been demoted from Admin!

❍ They no longer have admin powers
❍ They are now a regular member

ˏˋ°•*⁀➷ Pᴏᴡᴇʀᴇᴅ Bʏ ⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐ ➷⁀•°ˊˎ""",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ==================== CALLBACK HANDLER ====================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "main_menu":
        await send_main_menu(update, context, query)
        return
    
    elif data == "settings":
        text = f"⚙️ Settings Menu\n\n{get_owner_credit()}"
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=settings_menu())
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=settings_menu())
        return
    
    elif data == "help":
        text = """
📖 Powerfull Commands List 📖

═══════════════════════════

👑 Admin Commands:

/warn @user - Warn user
/unwarn @user - Remove warns
/warns @user - Check warns
/resetwarns @user - Reset warns
/mute @user - Mute user
/unmute @user - Unmute user
/kick @user - Kick user
/ban @user - Ban user
/unban @user - Unban user
/approve @user - Approve user
/unapprove @user - Remove approval
/reload - Reload admins
/settings - Change settings

👥 Role Commands:

/cofounder @user - Add Co-Founder
/uncofounder @user - Remove Co-Founder
/mod @user - Add Moderator
/unmod @user - Remove Moderator
/muter @user - Add Muter
/unmuter @user - Remove Muter
/cleaner @user - Add Cleaner
/uncleaner @user - Remove Cleaner
/helper @user - Add Helper
/unhelper @user - Remove Helper
/free @user - Add Free User
/unfree @user - Remove Free User
/roles - View all roles

📌 Pin Commands:

/pin - Pin a message
/unpin - Unpin message
/pinned - View pinned
/editpin - Edit pin
/delpin - Delete pin

🗑️ Delete Commands:

/del - Delete message
/logdel - Delete & log
/purge - Delete multiple

🔒 Lock/Unlock Commands:

/locktypes - Show lock types
/lock <type> - Lock message type
/unlock <type> - Unlock message type

📊 General Commands:

/start - Start bot
/help - Get help
/about - About bot
/ping - Bot status
/staff - View staff
/info - User info
/infopvt - Private info
/me - Your info
/geturl - Get message link
/sg @user - Show user's dark past
/history @user - Full history
/chat - Chat with bot

👋 Welcome & Goodbye:

/enablewelcome - Enable welcome
/disablewelcome - Disable welcome
/enablegoodbye - Enable goodbye
/disablegoodbye - Disable goodbye

🔰 Filter Commands:

/filter - Add filter
/stopfilter - Remove filter
/filters - List filters

═══════════════════════════

🔥 Powered By ── ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ──
"""
        try:
            await query.edit_message_text(text, parse_mode=None, reply_markup=back_button())
        except:
            await query.message.reply_text(text, parse_mode=None, reply_markup=back_button())
        return
    
    elif data == "about":
        text = f"""
⚡ About {Config.BOT_NAME} ⚡

────═◈═─ ✧◈✧ ─═◈═────
🤖 Name: {Config.BOT_NAME}  
📌 Username: {Config.BOT_USERNAME} 
👑 Owner: {Config.OWNER_NAME} 
📞 Contact: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 Description:
The Ultimate Group Management Bot

🔰 Status: Active

📢 For Updates: {Config.UPDATES_CHANNEL}
💬 Support: {Config.SUPPORT_GROUP}

{get_owner_credit()}
"""
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        return
    
    elif data == "staff":
        await query.edit_message_text("👥 Use /staff to view staff list!", parse_mode=ParseMode.HTML)
        return
    
    elif data == "sg":
        text = f"""
🔄 SG - User's Dark Past

Use /sg @username or reply to a user
To view their name and username change history!{get_owner_credit()}
"""
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML)
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    elif data == "history":
        text = f"""
📜 History Tracking

Use /history @username
To view their complete change history!{get_owner_credit()}
"""
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML)
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML)
        return
    
    elif data == "roles":
        try:
            await query.edit_message_text(
                f"👑 User Roles\n\nSelect a role to learn more:{get_owner_credit()}",
                parse_mode=ParseMode.HTML,
                reply_markup=role_menu()
            )
        except:
            await query.message.reply_text(
                f"👑 User Roles\n\nSelect a role to learn more:{get_owner_credit()}",
                parse_mode=ParseMode.HTML,
                reply_markup=role_menu()
            )
        return
    
    elif data == "stats":
        if user_id != Config.OWNER_ID:
            await query.answer("❌ Only owner can view stats!", show_alert=True)
            return
        
        stats = db.get_bot_stats()
        text = f"""
📊 Bot Statistics 📊

────═◈═─ ✧◈✧ ─═◈═────
❍ Users: {stats.get('users', 0)}  
❍ Groups: {stats.get('groups', 0)} 
❍ Warnings: {stats.get('warnings', 0)}   
❍ Active Mutes: {stats.get('mutes', 0)} 
❍ History: {stats.get('history', 0)}
❍ Filters: {stats.get('filters', 0)}
❍ Messages: {stats.get('messages', 0)}
────═◈═─ ✧◈✧ ─═◈═────
❍ Bot Info:
❍ Name: {Config.BOT_NAME}
❍ Version: 3.0.0
❍ Owner: {Config.OWNER_NAME}
❍ Status: Online

{get_owner_credit()}
"""
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        return
    
    elif data.startswith("set_"):
        setting = data.replace("set_", "")
        chat_id = update.effective_chat.id
        settings = db.get_settings(chat_id)
        current = settings.get(setting, True)
        db.update_settings(chat_id, setting, not current)
        
        text = f"✅ {setting.upper()} {'Enabled' if not current else 'Disabled'}!{get_owner_credit()}"
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=settings_menu())
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=settings_menu())
        return
    
    elif data.startswith("role_"):
        role_name = data.replace("role_", "").upper()
        descriptions = {
            "FOUNDER": "Group creator with all powers",
            "CO-FOUNDER": "Admin with extra power to manage staff",
            "ADMIN": "Group administrator",
            "MODERATOR": "Can moderate users with commands",
            "MUTER": "Can mute and unmute users",
            "CLEANER": "Can delete messages",
            "HELPER": "Appears in staff list",
            "FREE": "Ignored by automatic punishment"
        }
        desc = descriptions.get(role_name, "")
        text = f"""
👑 {role_name} Role

To add this role: /{role_name.lower()} @user
To remove this role: /un{role_name.lower()} @user

Description:
{desc}{get_owner_credit()}
"""
        try:
            await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        except:
            await query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=back_button())
        return

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_chat:
            await context.bot.send_message(
                update.effective_chat.id,
                f"❌ Error occurred!\n{str(context.error)[:100]}"
            )
    except:
        pass

# ==================== MAIN ====================
def main():
    if not Config.BOT_TOKEN:
        premium_print("Bot token not found!", "❌")
        sys.exit(1)
    
    try:
        app = Application.builder().token(Config.BOT_TOKEN).build()
        
        # General
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("about", about))
        app.add_handler(CommandHandler("ping", ping))
        app.add_handler(CommandHandler("staff", staff))
        app.add_handler(CommandHandler("info", info))
        app.add_handler(CommandHandler("infopvt", infopvt))
        app.add_handler(CommandHandler("me", me))
        app.add_handler(CommandHandler("geturl", geturl))
        app.add_handler(CommandHandler("chat", chat))
        
        # Lock/Unlock
        app.add_handler(CommandHandler("locktypes", locktypes))
        app.add_handler(CommandHandler("lock", lock))
        app.add_handler(CommandHandler("unlock", unlock))
        
        # Admin
        app.add_handler(CommandHandler("warn", warn))
        app.add_handler(CommandHandler("unwarn", unwarn))
        app.add_handler(CommandHandler("warns", warns))
        app.add_handler(CommandHandler("resetwarns", resetwarns))
        app.add_handler(CommandHandler("mute", mute))
        app.add_handler(CommandHandler("unmute", unmute))
        app.add_handler(CommandHandler("kick", kick))
        app.add_handler(CommandHandler("ban", ban))
        app.add_handler(CommandHandler("unban", unban))
        app.add_handler(CommandHandler("approve", approve))
        app.add_handler(CommandHandler("unapprove", unapprove))
        app.add_handler(CommandHandler("reload", reload))
        app.add_handler(CommandHandler("settings", settings))
        
        # Roles
        app.add_handler(CommandHandler("cofounder", lambda u, c: add_role(u, c, "cofounder")))
        app.add_handler(CommandHandler("uncofounder", lambda u, c: remove_role(u, c, "cofounder")))
        app.add_handler(CommandHandler("mod", lambda u, c: add_role(u, c, "mod")))
        app.add_handler(CommandHandler("unmod", lambda u, c: remove_role(u, c, "mod")))
        app.add_handler(CommandHandler("muter", lambda u, c: add_role(u, c, "muter")))
        app.add_handler(CommandHandler("unmuter", lambda u, c: remove_role(u, c, "muter")))
        app.add_handler(CommandHandler("cleaner", lambda u, c: add_role(u, c, "cleaner")))
        app.add_handler(CommandHandler("uncleaner", lambda u, c: remove_role(u, c, "cleaner")))
        app.add_handler(CommandHandler("helper", lambda u, c: add_role(u, c, "helper")))
        app.add_handler(CommandHandler("unhelper", lambda u, c: remove_role(u, c, "helper")))
        app.add_handler(CommandHandler("free", lambda u, c: add_role(u, c, "free")))
        app.add_handler(CommandHandler("unfree", lambda u, c: remove_role(u, c, "free")))
        app.add_handler(CommandHandler("roles", roles))
        
        # Pin
        app.add_handler(CommandHandler("pin", pin))
        app.add_handler(CommandHandler("unpin", unpin))
        app.add_handler(CommandHandler("pinned", pinned))
        app.add_handler(CommandHandler("editpin", editpin))
        app.add_handler(CommandHandler("delpin", delpin))
        
        # Delete
        app.add_handler(CommandHandler("del", delete_message))
        app.add_handler(CommandHandler("logdel", logdel))
        app.add_handler(CommandHandler("purge", purge))
        
        # History (SG and History)
        app.add_handler(CommandHandler("sg", sg))
        app.add_handler(CommandHandler("history", history))
        
        # Welcome & Goodbye
        app.add_handler(CommandHandler("enablewelcome", enablewelcome))
        app.add_handler(CommandHandler("disablewelcome", disablewelcome))
        app.add_handler(CommandHandler("enablegoodbye", enablegoodbye))
        app.add_handler(CommandHandler("disablegoodbye", disablegoodbye))
        
        # Filters
        app.add_handler(CommandHandler("filter", filter_add))
        app.add_handler(CommandHandler("stopfilter", stopfilter))
        app.add_handler(CommandHandler("filters", filters_list))
        
        # Promote/Demote
        app.add_handler(CommandHandler("promote", promote))
        app.add_handler(CommandHandler("demote", demote))
        
        # Message Handlers
        app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_handler))
        app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_handler))
        
        # Callback Handler
        app.add_handler(CallbackQueryHandler(callback_handler))
        
        # Error Handler
        app.add_error_handler(error_handler)
        
        premium_print(f"Bot {Config.BOT_NAME} is now running!", "⚡")
        premium_print(f"Owner: {Config.OWNER_NAME}", "👑")
        premium_print(f"Bot Username: {Config.BOT_USERNAME}", "📌")
        
        app.run_polling()
    except Exception as e:
        premium_print(f"Error: {str(e)}", "❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
