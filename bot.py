#!/usr/bin/env python3
"""
ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ - ᴘʀᴇᴍɪᴜᴍ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# ────═◈═─ FIX FOR PTB VERSION COMPATIBILITY ─═◈═────
# This fixes the '_Updater__polling_cleanup_cb' error
import telegram
if not hasattr(telegram.ext.Updater, '_Updater__polling_cleanup_cb'):
    # Add the missing attribute
    setattr(telegram.ext.Updater, '_Updater__polling_cleanup_cb', None)
    print("✅ Applied monkey patch for Updater")
# ──────────────────────────────────────────────────

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from telegram.constants import ParseMode

from config import Config
from database import Database

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Custom print with premium style
def premium_print(message, symbol="⚡"):
    border = "═" * 50
    timestamp = datetime.now().strftime("%H:%M:%S")
    styled_msg = f"""
╔{border}╗
║  {symbol} [{timestamp}] {message}
╚{border}╝
"""
    print(styled_msg)

class PikachuProtectionBot:
    def __init__(self):
        self.app = None
        premium_print(f"ʙᴏᴛ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ: {Config.BOT_NAME}", "🚀")
        premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
        premium_print(f"ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs: ʟᴏᴀᴅᴇᴅ", "💎")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.add_user(user.id, user.username, user.first_name)
        
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        keyboard = [
            [
                InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"),
                InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")
            ]
        ]
        
        if is_premium:
            keyboard.append([
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ])
        
        welcome_text = f"""
╔═══════════════════════════════════════╗
║     ⚡ ᴘɪᴋᴀᴄʜᴜ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ ⚡     ║
╚═══════════════════════════════════════╝

────═◈═─ ✧◈✧ ─═◈═────
  🤖 ɴᴀᴍᴇ: {Config.BOT_NAME}  
  📌 ɪᴅ: {Config.BOT_USERNAME} 
  👑 ᴏᴡɴᴇʀ: {Config.OWNER_NAME} 
  📞 ᴄᴏɴᴛᴀᴄᴛ: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

✨ **ᴡᴇʟᴄᴏᴍᴇ {user.first_name}!** ✨

ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ 
ᴡɪᴛʜ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ.

💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs:** {'✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}

📌 **ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!**

ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

╔═══════════════════════════╗

**👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /warn @username - ᴡᴀʀɴ ᴜsᴇʀ  
╰┈➤ /warns @username - ᴄʜᴇᴄᴋ ᴡᴀʀɴs  
╰┈➤ /resetwarns @username - ʀᴇsᴇᴛ ᴡᴀʀɴs  
╰┈➤ /mute @username - ᴍᴜᴛᴇ ᴜsᴇʀ  
╰┈➤ /unmute @username - ᴜɴᴍᴜᴛᴇ ᴜsᴇʀ  
╰┈➤ /kick @username - ᴋɪᴄᴋ ᴜsᴇʀ  
╰┈➤ /ban @username - ʙᴀɴ ᴜsᴇʀ  
╰┈➤ /unban @username - ᴜɴʙᴀɴ ᴜsᴇʀ  

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ  
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ  
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ  

**💎 ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /premium - ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ  

╚═══════════════════════════╝

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        about_text = f"""
⚡ **ᴀʙᴏᴜᴛ {Config.BOT_NAME}** ⚡

────═◈═─ ✧◈✧ ─═◈═────
  🤖 ɴᴀᴍᴇ: {Config.BOT_NAME}  
  📌 ɪᴅ: {Config.BOT_USERNAME} 
  👑 ᴏᴡɴᴇʀ: {Config.OWNER_NAME} 
  📞 ᴄᴏɴᴛᴀᴄᴛ: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────
✦•·································•✦

💫 **ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**
ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ ᴡɪᴛʜ 
ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ.

⚙️ **ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴀɴᴛɪ-ʟɪɴᴋ
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ
╰┈➤ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ
╰┈➤ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ

✦•·································•✦
ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.OWNER_NAME}
🙏 ᴊᴀʏ sʜʀᴇᴇ ʀᴀᴍ 🙏
"""
        await update.message.reply_text(about_text, parse_mode="Markdown")
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        if is_premium:
            text = f"""
💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs** 💎

✅ **ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!**

**ᴜɴʟᴏᴄᴋᴇᴅ ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ
╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ
╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs
╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ

✨ ᴛʜᴀɴᴋs ғᴏʀ ʙᴇɪɴɢ ᴘʀᴇᴍɪᴜᴍ!
"""
        else:
            text = f"""
💎 **ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ** 💎

**ᴜɴʟᴏᴄᴋ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ
╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ
╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs
╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ

**ᴘʀɪᴄᴇ:** $5/ᴍᴏɴᴛʜ

ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ᴛᴏ ʙᴜʏ:
📞 {Config.OWNER_USERNAME}
"""
        await update.message.reply_text(text, parse_mode="Markdown")
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data == "about":
            text = f"""
⚡ **ᴀʙᴏᴜᴛ {Config.BOT_NAME}** ⚡

────═◈═─ ✧◈✧ ─═◈═────
  🤖 ɴᴀᴍᴇ: {Config.BOT_NAME}  
  📌 ɪᴅ: {Config.BOT_USERNAME} 
  👑 ᴏᴡɴᴇʀ: {Config.OWNER_NAME} 
  📞 ᴄᴏɴᴛᴀᴄᴛ: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────
✦•·································•✦

💫 **ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**
ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ ᴡɪᴛʜ 
ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴇʀᴀᴛɪᴏɴ.

⚙️ **ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴀɴᴛɪ-ʟɪɴᴋ
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ
╰┈➤ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ
╰┈➤ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ

✦•·································•✦
ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.OWNER_NAME}
🙏 ᴊᴀʏ sʜʀᴇᴇ ʀᴀᴍ 🙏
"""
            await query.edit_message_text(text, parse_mode="Markdown")
        
        elif data == "help":
            text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

╔═══════════════════════════╗

**👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /warn @username - ᴡᴀʀɴ ᴜsᴇʀ  
╰┈➤ /warns @username - ᴄʜᴇᴄᴋ ᴡᴀʀɴs  
╰┈➤ /resetwarns @username - ʀᴇsᴇᴛ ᴡᴀʀɴs  
╰┈➤ /mute @username - ᴍᴜᴛᴇ ᴜsᴇʀ  
╰┈➤ /unmute @username - ᴜɴᴍᴜᴛᴇ ᴜsᴇʀ  
╰┈➤ /kick @username - ᴋɪᴄᴋ ᴜsᴇʀ  
╰┈➤ /ban @username - ʙᴀɴ ᴜsᴇʀ  
╰┈➤ /unban @username - ᴜɴʙᴀɴ ᴜsᴇʀ  

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ  
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ  
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ  

**💎 ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /premium - ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ  

╚═══════════════════════════╝

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
            await query.edit_message_text(text, parse_mode="Markdown")
        
        elif data == "stats":
            if user_id != Config.OWNER_ID:
                await query.edit_message_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!", parse_mode="Markdown")
                return
            
            users_count = db.users.count_documents({})
            groups_count = db.groups.count_documents({})
            warnings_count = db.warnings.count_documents({})
            mutes_count = db.mutes.count_documents({})
            premium_count = db.premium.count_documents({})
            
            text = f"""
📊 **ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs** 📊

────═◈═─ ✧◈✧ ─═◈═────
  👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {users_count}  
  📍 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs: {groups_count} 
  ⚠️ ᴡᴀʀɴɪɴɢs: {warnings_count}   
  🔇 ᴀᴄᴛɪᴠᴇ ᴍᴜᴛᴇs: {mutes_count} 
  💎 ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: {premium_count}
────═◈═─ ✧◈✧ ─═◈═────
✦•·································•✦

🔥 **ʙᴏᴛ ɪɴғᴏ:**
╰┈➤ ɴᴀᴍᴇ: {Config.BOT_NAME}
╰┈➤ ᴠᴇʀsɪᴏɴ: 2.0.0
╰┈➤ ᴏᴡɴᴇʀ: {Config.OWNER_NAME}

⚡ **sᴛᴀᴛᴜs:** ᴏɴʟɪɴᴇ
✦•·································•✦
"""
            await query.edit_message_text(text, parse_mode="Markdown")
        
        elif data == "settings":
            keyboard = [
                [
                    InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"),
                    InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")
                ],
                [
                    InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"),
                    InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_main")
                ]
            ]
            await query.edit_message_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "back_main":
            is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
            keyboard = [
                [
                    InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"),
                    InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")
                ],
                [
                    InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"),
                    InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")
                ]
            ]
            if is_premium:
                keyboard.append([
                    InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
                ])
            await query.edit_message_text("🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "premium":
            is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
            if is_premium:
                text = f"""
💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs** 💎

✅ **ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!**

**ᴜɴʟᴏᴄᴋᴇᴅ ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ
╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ
╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs
╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ

✨ ᴛʜᴀɴᴋs ғᴏʀ ʙᴇɪɴɢ ᴘʀᴇᴍɪᴜᴍ!
"""
            else:
                text = f"""
💎 **ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ** 💎

**ᴜɴʟᴏᴄᴋ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ
╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ
╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs
╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ

**ᴘʀɪᴄᴇ:** $5/ᴍᴏɴᴛʜ

ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ᴛᴏ ʙᴜʏ:
📞 {Config.OWNER_USERNAME}
"""
            await query.edit_message_text(text, parse_mode="Markdown")
        
        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            status = "ᴇɴᴀʙʟᴇᴅ" if not current else "ᴅɪsᴀʙʟᴇᴅ"
            await query.edit_message_text(f"✅ **{setting.upper()}** {status}!", parse_mode="Markdown")
            await asyncio.sleep(1)
            
            keyboard = [
                [
                    InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"),
                    InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")
                ],
                [
                    InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"),
                    InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_main")
                ]
            ]
            await query.edit_message_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "set_welcome":
            settings = await db.get_settings(update.effective_chat.id)
            current = settings.get('welcome', True)
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{'✅' if current else '❌'} ᴛᴏɢɢʟᴇ",
                        callback_data="toggle_welcome"
                    )
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
                ]
            ]
            await query.edit_message_text(
                f"👋 **ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ**\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "set_goodbye":
            settings = await db.get_settings(update.effective_chat.id)
            current = settings.get('goodbye', True)
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{'✅' if current else '❌'} ᴛᴏɢɢʟᴇ",
                        callback_data="toggle_goodbye"
                    )
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
                ]
            ]
            await query.edit_message_text(
                f"👋 **ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ**\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "set_antispam":
            settings = await db.get_settings(update.effective_chat.id)
            current = settings.get('antispam', True)
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{'✅' if current else '❌'} ᴛᴏɢɢʟᴇ",
                        callback_data="toggle_antispam"
                    )
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
                ]
            ]
            await query.edit_message_text(
                f"🛡️ **ᴀɴᴛɪ-sᴘᴀᴍ**\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif data == "set_antilink":
            settings = await db.get_settings(update.effective_chat.id)
            current = settings.get('antilink', False)
            keyboard = [
                [
                    InlineKeyboardButton(
                        f"{'✅' if current else '❌'} ᴛᴏɢɢʟᴇ",
                        callback_data="toggle_antilink"
                    )
                ],
                [
                    InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")
                ]
            ]
            await query.edit_message_text(
                f"🔗 **ᴀɴᴛɪ-ʟɪɴᴋ**\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    update.effective_chat.id,
                    "❌ **ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!**\n"
                    f"ᴇʀʀᴏʀ: `{str(context.error)[:100]}`",
                    parse_mode="Markdown"
                )
        except:
            pass
    
    def run(self):
        try:
            self.app = Application.builder().token(Config.BOT_TOKEN).build()
            self.app.add_handler(CommandHandler("start", self.start))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("about", self.about_command))
            self.app.add_handler(CommandHandler("premium", self.premium_command))
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            self.app.add_error_handler(self.error_handler)
            
            premium_print(f"ʙᴏᴛ {Config.BOT_NAME} ɪs ɴᴏᴡ ʀᴜɴɴɪɴɢ!", "⚡")
            premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
            
            self.app.run_polling()
        except Exception as e:
            premium_print(f"ᴇʀʀᴏʀ: {str(e)}", "❌")
            sys.exit(1)

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        premium_print("ʙᴏᴛ ᴛᴏᴋᴇɴ ɴᴏᴛ ғᴏᴜɴᴅ!", "❌")
        sys.exit(1)
    
    bot = PikachuProtectionBot()
    bot.run()
