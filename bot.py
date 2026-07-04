#!/usr/bin/env python3
"""
ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ - ᴘʀᴇᴍɪᴜᴍ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ
"""

import os
import sys
import asyncio
import logging
import threading
from datetime import datetime
from flask import Flask

# ────═◈═─ FLASK WEB SERVER FOR RAILWAY ─═◈═────
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
print("🌐 Web server started for Railway port binding")
# ──────────────────────────────────────────────────

# ────═◈═─ IMPORT TELEGRAM ─═◈═────
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
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
    
    # ────═◈═─ START COMMAND ─═◈═────
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
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
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

ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ.

💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs:** {'✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}

📌 **ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!**

ᴜsᴇ /help ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    
    # ────═◈═─ HELP COMMAND ─═◈═────
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
    
    # ────═◈═─ ABOUT COMMAND ─═◈═────
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        about_text = f"""
⚡ **ᴀʙᴏᴜᴛ {Config.BOT_NAME}** ⚡

────═◈═─ ✧◈✧ ─═◈═────
  🤖 ɴᴀᴍᴇ: {Config.BOT_NAME}  
  📌 ɪᴅ: {Config.BOT_USERNAME} 
  👑 ᴏᴡɴᴇʀ: {Config.OWNER_NAME} 
  📞 ᴄᴏɴᴛᴀᴄᴛ: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 **ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**
ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ.

⚙️ **ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴀɴᴛɪ-ʟɪɴᴋ
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ
╰┈➤ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ
"""
        await update.message.reply_text(about_text, parse_mode="Markdown")
    
    # ────═◈═─ PREMIUM COMMAND ─═◈═────
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
    
    # ────═◈═─ MODERATION COMMANDS ─═◈═────
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warn command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴡᴀʀɴ!")
                return
        except:
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        # Get target user
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ᴡᴀʀɴ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        await db.add_warning(target.id, chat.id, reason, user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        warn_count = len(warnings)
        max_warns = Config.MAX_WARNINGS
        
        warn_msg = f"""
⚠️ **ᴡᴀʀɴɪɴɢ!** ⚠️

────═◈═─ ✧◈✧ ─═◈═────
  👤 {target.first_name}
  📊 ᴡᴀʀɴ: {warn_count}/{max_warns}
  📝 ʀᴇᴀsᴏɴ: {reason}
────═◈═─ ✧◈✧ ─═◈═────
"""
        await update.message.reply_text(warn_msg, parse_mode="Markdown")
        
        if warn_count >= max_warns:
            mute_duration = Config.MUTE_DURATION
            await db.add_mute(target.id, chat.id, mute_duration, f"ᴇxᴄᴇᴇᴅᴇᴅ ᴡᴀʀɴ ʟɪᴍɪᴛ", user.id)
            try:
                await context.bot.restrict_chat_member(
                    chat.id,
                    target.id,
                    ChatPermissions(can_send_messages=False)
                )
                mute_msg = f"""
🔇 **ᴀᴜᴛᴏ-ᴍᴜᴛᴇᴅ!** 🔇

────═◈═─ ✧◈✧ ─═◈═────
  👤 {target.first_name}
  ⏱️ {mute_duration}s
  📝 ʀᴇᴀsᴏɴ: ᴇxᴄᴇᴇᴅᴇᴅ ᴡᴀʀɴ ʟɪᴍɪᴛ
────═◈═─ ✧◈✧ ─═◈═────
"""
                await update.message.reply_text(mute_msg, parse_mode="Markdown")
            except:
                pass
    
    async def warns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warns command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        warnings = await db.get_warnings(target.id, chat.id)
        
        if not warnings:
            await update.message.reply_text(f"✅ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs!")
            return
        
        warn_text = f"⚠️ **ᴡᴀʀɴɪɴɢs ғᴏʀ {target.first_name}:**\n\n"
        for i, warn in enumerate(warnings, 1):
            warn_text += f"└ {i}. {warn['reason']}\n"
        
        await update.message.reply_text(warn_text, parse_mode="Markdown")
    
    async def reset_warns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resetwarns command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇsᴇᴛ ᴡᴀʀɴs!")
                return
        except:
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        await db.clear_warnings(target.id, chat.id)
        await update.message.reply_text(f"✅ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ ᴡᴀʀɴɪɴɢs ғᴏʀ {target.first_name}!")
    
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mute command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴜᴛᴇ!")
                return
        except:
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        duration = Config.MUTE_DURATION
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        await db.add_mute(target.id, chat.id, duration, reason, user.id)
        try:
            await context.bot.restrict_chat_member(
                chat.id,
                target.id,
                ChatPermissions(can_send_messages=False)
            )
            mute_msg = f"""
🔇 **ᴍᴜᴛᴇᴅ!** 🔇

────═◈═─ ✧◈✧ ─═◈═────
  👤 {target.first_name}
  ⏱️ {duration}s
  📝 ʀᴇᴀsᴏɴ: {reason}
────═◈═─ ✧◈✧ ─═◈═────
"""
            await update.message.reply_text(mute_msg, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unmute command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇ!")
                return
        except:
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        await db.remove_mute(target.id, chat.id)
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
            await update.message.reply_text(f"🔊 **ᴜɴᴍᴜᴛᴇᴅ {target.first_name}!**", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /kick command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴋɪᴄᴋ!")
                return
        except:
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"👢 **ᴋɪᴄᴋᴇᴅ {target.first_name}!**\n📝 ʀᴇᴀsᴏɴ: {reason}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ban command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʙᴀɴ!")
                return
        except:
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"🚫 **ʙᴀɴɴᴇᴅ {target.first_name}!**\n📝 ʀᴇᴀsᴏɴ: {reason}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴ!")
                return
        except:
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ!")
            return
        
        try:
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"✅ **ᴜɴʙᴀɴɴᴇᴅ {target.first_name}!**", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    # ────═◈═─ STATS COMMAND ─═◈═────
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != Config.OWNER_ID:
            await update.message.reply_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!")
            return
        
        users_count = db.users.count_documents({})
        groups_count = db.groups.count_documents({})
        warnings_count = db.warnings.count_documents({})
        mutes_count = db.mutes.count_documents({})
        premium_count = db.premium.count_documents({})
        
        stats_text = f"""
📊 **ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs** 📊

────═◈═─ ✧◈✧ ─═◈═────
  👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {users_count}  
  📍 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs: {groups_count} 
  ⚠️ ᴡᴀʀɴɪɴɢs: {warnings_count}   
  🔇 ᴀᴄᴛɪᴠᴇ ᴍᴜᴛᴇs: {mutes_count} 
  💎 ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: {premium_count}
────═◈═─ ✧◈✧ ─═◈═────
🔥 **ʙᴏᴛ ɪɴғᴏ:**
╰┈➤ ɴᴀᴍᴇ: {Config.BOT_NAME}
╰┈➤ ᴠᴇʀsɪᴏɴ: 2.0.0
╰┈➤ ᴏᴡɴᴇʀ: {Config.OWNER_NAME}
⚡ **sᴛᴀᴛᴜs:** ᴏɴʟɪɴᴇ
"""
        await update.message.reply_text(stats_text, parse_mode="Markdown")
    
    # ────═◈═─ CALLBACK HANDLER ─═◈═────
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
        
        # ────═◈═─ MAIN MENU ─═◈═────
        if data == "main_menu":
            keyboard = [
                [InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")],
                [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")]
            ]
            if is_premium:
                keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
            await query.edit_message_text("🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ ABOUT ─═◈═────
        elif data == "about":
            text = f"""
⚡ **ᴀʙᴏᴜᴛ {Config.BOT_NAME}** ⚡

────═◈═─ ✧◈✧ ─═◈═────
  🤖 ɴᴀᴍᴇ: {Config.BOT_NAME}  
  📌 ɪᴅ: {Config.BOT_USERNAME} 
  👑 ᴏᴡɴᴇʀ: {Config.OWNER_NAME} 
  📞 ᴄᴏɴᴛᴀᴄᴛ: {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

⚙️ **ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴀɴᴛɪ-ʟɪɴᴋ
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ HELP ─═◈═────
        elif data == "help":
            text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

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
╰┈➤ /premium - ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ  

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ STATS ─═◈═────
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
🔥 **ʙᴏᴛ ɪɴғᴏ:**
╰┈➤ ɴᴀᴍᴇ: {Config.BOT_NAME}
╰┈➤ ᴠᴇʀsɪᴏɴ: 2.0.0
╰┈➤ ᴏᴡɴᴇʀ: {Config.OWNER_NAME}
⚡ **sᴛᴀᴛᴜs:** ᴏɴʟɪɴᴇ
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ SETTINGS ─═◈═────
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
            ]
            await query.edit_message_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ PREMIUM ─═◈═────
        elif data == "premium":
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
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ SETTINGS TOGGLES ─═◈═────
        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            await query.edit_message_text(f"✅ **{setting.upper()}** {'ᴇɴᴀʙʟᴇᴅ' if not current else 'ᴅɪsᴀʙʟᴇᴅ'}!", parse_mode="Markdown")
            await asyncio.sleep(1)
            keyboard = [
                [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
            ]
            await query.edit_message_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data in ["set_welcome", "set_goodbye", "set_antispam", "set_antilink"]:
            setting_map = {
                "set_welcome": "welcome",
                "set_goodbye": "goodbye",
                "set_antispam": "antispam",
                "set_antilink": "antilink"
            }
            setting = setting_map.get(data, "welcome")
            settings = await db.get_settings(update.effective_chat.id)
            current = settings.get(setting, True)
            keyboard = [
                [InlineKeyboardButton(f"{'✅' if current else '❌'} ᴛᴏɢɢʟᴇ", callback_data=f"toggle_{setting}")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]
            display_name = data.replace("set_", "").upper()
            await query.edit_message_text(
                f"{display_name}\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    # ────═◈═─ ERROR HANDLER ─═◈═────
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
    
    # ────═◈═─ RUN BOT ─═◈═────
    def run(self):
        try:
            self.app = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Command handlers
            self.app.add_handler(CommandHandler("start", self.start))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("about", self.about_command))
            self.app.add_handler(CommandHandler("premium", self.premium_command))
            self.app.add_handler(CommandHandler("stats", self.stats_command))
            
            # Moderation commands
            self.app.add_handler(CommandHandler("warn", self.warn_command))
            self.app.add_handler(CommandHandler("warns", self.warns_command))
            self.app.add_handler(CommandHandler("resetwarns", self.reset_warns))
            self.app.add_handler(CommandHandler("mute", self.mute_command))
            self.app.add_handler(CommandHandler("unmute", self.unmute_command))
            self.app.add_handler(CommandHandler("kick", self.kick_command))
            self.app.add_handler(CommandHandler("ban", self.ban_command))
            self.app.add_handler(CommandHandler("unban", self.unban_command))
            
            # Callback handler
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            
            # Error handler
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
