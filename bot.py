#!/usr/bin/env python3
"""
⚡ PIKACHU X PROTECTION BOT - ULTIMATE GROUP MANAGEMENT ⚡
More Powerful Than Any Bot
"""

import os
import sys
import asyncio
import logging
import threading
import re
import json
import psutil
import platform
import time
from datetime import datetime, timedelta
from flask import Flask
from typing import Dict, List, Optional, Any

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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, User, ChatMember
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import Config
from database import Database

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
LOG_CHANNEL = -1003424504397

# ────═◈═─ FANCY TEXT CONVERTER ─═◈═────
def fancy_text(text):
    """Convert text to fancy Unicode style"""
    fancy_chars = {
        'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ',
        'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ',
        'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
        'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join(fancy_chars.get(char, char) for char in text)

def premium_print(message, symbol="⚡"):
    border = "═" * 50
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"""
╔{border}╗
║  {symbol} [{timestamp}] {message}
╚{border}╝
""")

class PikachuProtectionBot:
    def __init__(self):
        self.app = None
        self.user_message_cache = {}
        self.log_channel = LOG_CHANNEL
        self.start_time = datetime.now()
        self.bot_added_groups = {}
        premium_print(f"ʙᴏᴛ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ: {Config.BOT_NAME}", "🚀")
        premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
        premium_print(f"ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs: ʟᴏᴀᴅᴇᴅ", "💎")

    # ────═◈═─ HELPER FUNCTIONS ─═◈═────
    async def is_admin(self, context, chat_id, user_id):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except:
            return False

    async def is_owner(self, context, chat_id, user_id):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status == 'creator'
        except:
            return False

    async def is_founder(self, context, chat_id, user_id):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status == 'creator'
        except:
            return False

    async def get_user_role(self, user_id, chat_id):
        """Get user's role in the group"""
        role_data = await db.get_user_role(user_id, chat_id)
        if role_data:
            return role_data.get('role', 'Member')
        
        try:
            member = await self.app.bot.get_chat_member(chat_id, user_id)
            if member.status == 'creator':
                return 'Founder'
            elif member.status == 'administrator':
                return 'Admin'
        except:
            pass
        return 'Member'

    async def is_mod(self, context, chat_id, user_id):
        """Check if user has moderator permissions"""
        role = await self.get_user_role(user_id, chat_id)
        mod_roles = ['Founder', 'Co-Founder', 'Admin', 'Moderator', 'Muter']
        return role in mod_roles

    async def is_cleaner(self, context, chat_id, user_id):
        role = await self.get_user_role(user_id, chat_id)
        cleaner_roles = ['Founder', 'Co-Founder', 'Admin', 'Chat Cleaner']
        return role in cleaner_roles

    async def is_free(self, context, chat_id, user_id):
        role = await self.get_user_role(user_id, chat_id)
        free_roles = ['Founder', 'Co-Founder', 'Admin', 'Moderator', 'Muter', 'Free']
        return role in free_roles

    async def log_action(self, chat_id, message):
        if self.log_channel:
            try:
                await self.app.bot.send_message(self.log_channel, message, parse_mode="HTML")
            except:
                pass

    def get_footer(self):
        return f"\n\n╰┈➤ <b>Cʀᴇᴀᴛᴇᴅ ʙʏ {Config.OWNER_NAME}</b>"

    def get_owner_credit(self):
        return f"\n\n<b>👑 Cʀᴇᴀᴛᴇᴅ ʙʏ: {Config.OWNER_NAME}</b>"

    # ────═◈═─ CHECK BOT ADDED ─═◈═────
    async def check_bot_added(self, chat_id):
        """Check if bot is added to the group"""
        try:
            bot_member = await self.app.bot.get_chat_member(chat_id, self.app.bot.id)
            if bot_member.status in ['administrator', 'creator', 'member']:
                return True
        except:
            pass
        return False

    async def bot_added_checker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if bot is added and send warning if not"""
        chat = update.effective_chat
        if chat.type not in ['group', 'supergroup']:
            return
        
        chat_id = chat.id
        
        is_added = await self.check_bot_added(chat_id)
        
        if not is_added:
            keyboard = [[
                InlineKeyboardButton(
                    "🔗 Kɪᴅɴᴀᴘ Mᴇ - Aᴅᴅ Tᴏ Gʀᴏᴜᴘ", 
                    url=f"https://t.me/{context.bot.username}?startgroup=start"
                )
            ]]
            
            warning_msg = f"""
╔═══════════════════════════════════╗
║  ⚠️ <b>Bᴏᴛ Nᴏᴛ Aᴅᴅᴇᴅ Yᴇᴛ!</b> ⚠️
╚═══════════════════════════════════╝

Hᴇʏ {chat.title}!

Tᴏ ᴜsᴇ ᴍʏ ᴘᴏᴡᴇʀғᴜʟ ғᴇᴀᴛᴜʀᴇs, 
ʏᴏᴜ ᴍᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ғɪʀsᴛ!

<b>📌 Hᴏᴡ ᴛᴏ ᴀᴅᴅ ᴍᴇ:</b>
1️⃣ Cʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ
2️⃣ Sᴇʟᴇᴄᴛ ᴛʜɪs ɢʀᴏᴜᴘ
3️⃣ Mᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ
4️⃣ I'ʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ sᴛᴀʀᴛ ᴡᴏʀᴋɪɴɢ!

<b>💡 Pʀᴏ Tɪᴘ:</b> Gɪᴠᴇ ᴍᴇ ᴀʟʟ ᴘᴇʀᴍɪssɪᴏɴs ғᴏʀ ʙᴇsᴛ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ!
{self.get_footer()}
"""
            try:
                await update.message.reply_text(
                    warning_msg,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
            return False
        
        return True

    # ────═◈═─ USER ROLE MANAGEMENT ─═◈═────
    async def set_user_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE, role: str, action: str):
        """Set or remove user role"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        user_role = await self.get_user_role(user.id, chat.id)
        allowed_roles = ['Founder', 'Co-Founder']
        
        if user_role not in allowed_roles and user.id != Config.OWNER_ID:
            await update.message.reply_text(f"❌ Oɴʟʏ Fᴏᴜɴᴅᴇʀ ᴀɴᴅ Cᴏ-Fᴏᴜɴᴅᴇʀ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʀᴏʟᴇs!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text(f"⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        
        if target.is_bot:
            await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴍᴀɴᴀɢᴇ ʀᴏʟᴇs ғᴏʀ ʙᴏᴛs!")
            return
        
        if target.id == user.id:
            await update.message.reply_text("❌ Yᴏᴜ ᴄᴀɴ'ᴛ ᴄʜᴀɴɢᴇ ʏᴏᴜʀ ᴏᴡɴ ʀᴏʟᴇ!")
            return
        
        if action == "add":
            await db.set_user_role(target.id, chat.id, role)
            await update.message.reply_text(
                f"✅ <b>{role} ʀᴏʟᴇ ᴀᴅᴅᴇᴅ ᴛᴏ {target.first_name}!</b>\n\n"
                f"📌 <b>Rᴏʟᴇ:</b> {role}\n"
                f"👤 <b>Uꜱᴇʀ:</b> {target.first_name}\n"
                f"🆔 <b>ID:</b> <code>{target.id}</code>{self.get_footer()}",
                parse_mode="HTML"
            )
            await self.log_action(chat.id, f"➕ <b>{role}</b> ᴀᴅᴅᴇᴅ ᴛᴏ {target.first_name} ʙʏ {user.first_name}")
        else:
            await db.remove_user_role(target.id, chat.id)
            await update.message.reply_text(
                f"✅ <b>{role} ʀᴏʟᴇ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ {target.first_name}!</b>\n\n"
                f"📌 <b>Rᴏʟᴇ:</b> {role}\n"
                f"👤 <b>Uꜱᴇʀ:</b> {target.first_name}\n"
                f"🆔 <b>ID:</b> <code>{target.id}</code>{self.get_footer()}",
                parse_mode="HTML"
            )
            await self.log_action(chat.id, f"➖ <b>{role}</b> ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ {target.first_name} ʙʏ {user.first_name}")

    # ────═◈═─ ROLE COMMANDS ─═◈═────
    async def cofounder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Co-Founder", "add")
    
    async def uncofounder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Co-Founder", "remove")
    
    async def moderator_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Moderator", "add")
    
    async def unmoderator_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Moderator", "remove")
    
    async def muter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Muter", "add")
    
    async def unmuter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Muter", "remove")
    
    async def cleaner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Chat Cleaner", "add")
    
    async def uncleaner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Chat Cleaner", "remove")
    
    async def helper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Helper", "add")
    
    async def unhelper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Helper", "remove")
    
    async def free_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Free", "add")
    
    async def unfree_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.set_user_role(update, context, "Free", "remove")

    # ────═◈═─ USER HISTORY TRACKING ─═◈═────
    async def track_user_history(self, user: User):
        try:
            current_data = {
                'first_name': user.first_name,
                'last_name': user.last_name or '',
                'username': user.username,
                'timestamp': datetime.now().isoformat()
            }
            history = await db.get_user_history(user.id)
            changed = False
            if history:
                last = history[-1]
                if (last.get('first_name') != current_data['first_name'] or
                    last.get('username') != current_data['username']):
                    changed = True
            else:
                changed = True
            if changed:
                await db.add_user_history(user.id, current_data)
        except Exception as e:
            logger.error(f"Error tracking user history: {e}")

    # ────═◈═─ SG COMMAND ─═◈═────
    async def sg_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        if not target:
            await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        history = await db.get_user_history(target.id)
        user_stats = await db.get_user_stats(target.id)
        role = await self.get_user_role(target.id, chat.id)
        
        if not history:
            msg = f"""
📋 <b>HISTORY FOR {target.id}</b>

<b>Nᴀᴍᴇs</b>
Nᴏ ʜɪsᴛᴏʀʏ ʀᴇᴄᴏʀᴅᴇᴅ ʏᴇᴛ!

<b>Uꜱᴇʀɴᴀᴍᴇs</b>
Nᴏ ʜɪsᴛᴏʀʏ ʀᴇᴄᴏʀᴅᴇᴅ ʏᴇᴛ!

<b>Rᴏʟᴇ:</b> {role}
{self.get_footer()}
"""
            await update.message.reply_text(msg, parse_mode="HTML")
            return
        
        names = []
        usernames = []
        
        for entry in history:
            timestamp = entry.get('timestamp', 'Unknown')
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("[%d/%m/%y %H:%M:%S]")
            except:
                pass
            
            name = entry.get('first_name', 'Unknown')
            username = entry.get('username', '')
            
            names.append({
                'timestamp': timestamp,
                'name': name
            })
            
            if username:
                usernames.append({
                    'timestamp': timestamp,
                    'username': f"@{username}"
                })
        
        msg = f"""
📋 <b>HISTORY FOR {target.id}</b>

<b>Nᴀᴍᴇs</b>
"""
        
        for i, entry in enumerate(names[:20], 1):
            msg += f"{i:02d}. {entry['timestamp']} {entry['name']}\n"
        
        if len(names) > 20:
            msg += f"\n... ᴀɴᴅ {len(names) - 20} ᴍᴏʀᴇ ᴄʜᴀɴɢᴇs\n"
        
        msg += f"\n<b>Uꜱᴇʀɴᴀᴍᴇs</b>\n"
        
        if usernames:
            for i, entry in enumerate(usernames[:20], 1):
                username_display = entry['username'] if entry['username'] else '(ᴇᴍᴘᴛʏ)'
                msg += f"{i}. {entry['timestamp']} {username_display}\n"
            if len(usernames) > 20:
                msg += f"\n... ᴀɴᴅ {len(usernames) - 20} ᴍᴏʀᴇ ᴄʜᴀɴɢᴇs\n"
        else:
            msg += "Nᴏ ᴜsᴇʀɴᴀᴍᴇ ʜɪsᴛᴏʀʏ ʀᴇᴄᴏʀᴅᴇᴅ!\n"
        
        msg += f"\n📊 <b>Tᴏᴛᴀʟ Nᴀᴍᴇ Cʜᴀɴɢᴇs:</b> {len(names)}"
        msg += f"\n📊 <b>Tᴏᴛᴀʟ Uꜱᴇʀɴᴀᴍᴇ Cʜᴀɴɢᴇs:</b> {len(usernames)}"
        msg += f"\n📊 <b>Tᴏᴛᴀʟ Mᴇssᴀɢᴇs:</b> {user_stats.get('messages', 0)}"
        msg += f"\n👑 <b>Rᴏʟᴇ:</b> {role}"
        msg += self.get_footer()
        
        await update.message.reply_text(msg, parse_mode="HTML")

    # ────═◈═─ MAIN MENU ─═◈═────
    async def get_main_menu_message(self, user, is_premium):
        user_stats = await db.get_user_stats(user.id)
        history_count = len(await db.get_user_history(user.id))
        
        return f"""
╔═══════════════════════════════════╗
║  ⚡ <b>PIKACHU PROTECTION BOT</b> ⚡
╚═══════════════════════════════════╝

✨ <b>Hᴇʟʟᴏ {user.first_name}!</b> ✨

I ᴀᴍ ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ!

<b>📊 Yᴏᴜʀ Sᴛᴀᴛs:</b>
╰┈➤ 👥 Gʀᴏᴜᴘs: {user_stats.get('groups', 0)}
╰┈➤ 🔄 Nᴀᴍᴇ Cʜᴀɴɢᴇs: {history_count}
╰┈➤ 📝 Tᴏᴛᴀʟ Mᴇssᴀɢᴇs: {user_stats.get('messages', 0)}

<b>🔰 Pᴏᴡᴇʀғᴜʟ Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ 🛡️ Aɴᴛɪ-Sᴘᴀᴍ & Lɪɴᴋ Sʜɪᴇʟᴅ
╰┈➤ ⚠️ Wᴀʀɴ/Mᴜᴛᴇ/Bᴀɴ/Kɪᴄᴋ
╰┈➤ 📌 Pɪɴ/Uɴᴘɪɴ/Dᴇʟᴇᴛᴇ/Pᴜʀɢᴇ
╰┈➤ 👋 Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ
╰┈➤ 👥 Aᴅᴠᴀɴᴄᴇᴅ Rᴏʟᴇs Sʏsᴛᴇᴍ
╰┈➤ 📊 Sᴛᴀғғ Lɪsᴛ & Sᴛᴀᴛs
╰┈➤ 📋 Cᴜsᴛᴏᴍ Rᴜʟᴇs
╰┈➤ 🔄 SG (Uꜱᴇʀ Hɪsᴛᴏʀʏ)
╰┈➤ 📜 Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ
╰┈➤ 💬 Sᴍᴀʀᴛ Cʜᴀᴛ
╰┈➤ 💎 Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs

💎 <b>Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs:</b> {'✅ Aᴄᴛɪᴠᴇ' if is_premium else '❌ Iɴᴀᴄᴛɪᴠᴇ'}

📌 <b>Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!</b>
{self.get_owner_credit()}
"""

    # ────═◈═─ START COMMAND ─═◈═────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.add_user(user.id, user.username, user.first_name)
        await self.track_user_history(user)
        
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        if update.effective_chat.type in ['group', 'supergroup']:
            is_added = await self.bot_added_checker(update, context)
            if not is_added:
                return
        
        welcome_text = await self.get_main_menu_message(user, is_premium)
        
        keyboard = [
            [InlineKeyboardButton("📊 Sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ Sᴇᴛᴛɪɴɢs", callback_data="settings")],
            [InlineKeyboardButton("📖 Hᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ Aʙᴏᴜᴛ", callback_data="about")],
            [InlineKeyboardButton("👥 Sᴛᴀғғ", callback_data="staff"), InlineKeyboardButton("🔄 SG", callback_data="sg")],
            [InlineKeyboardButton("📜 Hɪsᴛᴏʀʏ", callback_data="history"), InlineKeyboardButton("💬 Cʜᴀᴛ", callback_data="chat")],
            [InlineKeyboardButton("👑 Rᴏʟᴇs", callback_data="roles")],
            [InlineKeyboardButton("🔗 Kɪᴅɴᴀᴘ Mᴇ - Aᴅᴅ Tᴏ Gʀᴏᴜᴘ", url=f"https://t.me/{context.bot.username}?startgroup=start")]
        ]
        if is_premium:
            keyboard.append([InlineKeyboardButton("💎 Pʀᴇᴍɪᴜᴍ", callback_data="premium")])
        
        photo_url = "https://i.ibb.co/7NT4SDXy/file-124.jpg"
        
        try:
            await update.message.reply_photo(
                photo=photo_url,
                caption=welcome_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Photo send failed: {e}")
            await update.message.reply_text(
                welcome_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # ────═◈═─ WELCOME HANDLER ─═◈═────
    async def welcome_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.new_chat_members:
            return
        
        chat = update.effective_chat
        chat_id = chat.id
        chat_title = chat.title or "Unknown Group"
        
        logger.info(f"Welcome handler triggered in {chat_title} ({chat_id})")
        
        if not await self.check_bot_added(chat_id):
            return
        
        try:
            settings = await db.get_settings(chat_id)
            if not settings.get('welcome', True):
                return
        except:
            pass
        
        for member in update.message.new_chat_members:
            if member.is_bot:
                continue
            
            try:
                await db.add_user(member.id, member.username, member.first_name)
                await self.track_user_history(member)
                
                try:
                    member_count = await context.bot.get_chat_member_count(chat_id)
                except:
                    member_count = "?"
                
                try:
                    user_full = await context.bot.get_chat(member.id)
                    user_bio = getattr(user_full, 'bio', 'No bio set')
                    user_name = member.first_name or "N/A"
                    user_username = f"@{member.username}" if member.username else "No username"
                except:
                    user_name = member.first_name or "N/A"
                    user_username = "No username"
                    user_bio = "No bio set"
                
                photo_file_id = None
                try:
                    photos = await context.bot.get_user_profile_photos(member.id, limit=1)
                    if photos.total_count > 0:
                        photo_file_id = photos.photos[0][-1].file_id
                except:
                    pass
                
                role = "👤 Member"
                try:
                    chat_member = await context.bot.get_chat_member(chat_id, member.id)
                    if chat_member.status == 'creator':
                        role = "👑 Founder"
                    elif chat_member.status == 'administrator':
                        role = "👔 Admin"
                    else:
                        role = await self.get_user_role(member.id, chat_id)
                        role = f"👤 {role}" if role != 'Member' else "👤 Member"
                except:
                    pass
                
                welcome_msg = f"""
╔═══════════════════════════════════╗
║  <b>WELCOME TO THE PARTY!</b> ║
╚═══════════════════════════════════╝

<b>NAME:</b> <code>{user_name}</code>
<b>ID:</b> <code>{member.id}</code>
<b>USERNAME:</b> <code>{user_username}</code>
<b>BIO:</b> <i>{user_bio[:100] if user_bio != 'No bio set' else 'No bio set'}</i>

╔═══════════════════════════════════╗
<b>GROUP:</b> {chat_title}
<b>TOTAL MEMBERS:</b> {member_count}
<b>STATUS:</b> {role}
╚═══════════════════════════════════╝

Yᴏᴜ ᴡᴏɴ'ᴛ ʟᴇᴀᴠᴇ ᴍᴇ, ʀɪɢʜᴛ...?
I'ᴍ ɴᴏᴛ ᴀ ʜᴜᴍᴀɴ...
{self.get_owner_credit()}
"""
                
                try:
                    if photo_file_id:
                        await context.bot.send_photo(
                            chat_id,
                            photo=photo_file_id,
                            caption=welcome_msg,
                            parse_mode="HTML"
                        )
                    else:
                        await context.bot.send_message(
                            chat_id,
                            welcome_msg,
                            parse_mode="HTML"
                        )
                except Exception as e:
                    logger.error(f"Error sending welcome: {e}")
                    
            except Exception as e:
                logger.error(f"Error processing member {member.id}: {e}")

    # ────═◈═─ PREMIUM COMMAND ─═◈═────
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show premium status and features"""
        user = update.effective_user
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        if is_premium:
            text = f"""
💎 <b>Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs</b> 💎

✅ <b>Yᴏᴜ ᴀʀᴇ ᴀ Pʀᴇᴍɪᴜᴍ Uꜱᴇʀ!</b>

<b>Uɴʟᴏᴄᴋᴇᴅ Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ Aɴᴛɪ-Cʀᴀsʜ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴛɪ-Sᴘᴀᴍ
╰┈➤ Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ GɪF
╰┈➤ Pʀɪᴠᴀᴛᴇ Lᴏɢs
╰┈➤ 24/7 Sᴜᴘᴘᴏʀᴛ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴀʟʏᴛɪᴄs
╰┈➤ Cᴜsᴛᴏᴍ Cᴏᴍᴍᴀɴᴅs

{self.get_owner_credit()}
"""
        else:
            text = f"""
💎 <b>Pʀᴇᴍɪᴜᴍ Pʟᴀɴ</b> 💎

<b>Uɴʟᴏᴄᴋ Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ Aɴᴛɪ-Cʀᴀsʜ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴛɪ-Sᴘᴀᴍ
╰┈➤ Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ GɪF
╰┈➤ Pʀɪᴠᴀᴛᴇ Lᴏɢs
╰┈➤ 24/7 Sᴜᴘᴘᴏʀᴛ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴀʟʏᴛɪᴄs
╰┈➤ Cᴜsᴛᴏᴍ Cᴏᴍᴍᴀɴᴅs

<b>Pʀɪᴄᴇ:</b> $5/ᴍᴏɴᴛʜ

Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ Tᴏ Bᴜʏ:
📞 {Config.OWNER_USERNAME}

{self.get_owner_credit()}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ HELP COMMAND ─═◈═────
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""
╔═══════════════════════════════════════════╗
║  📖 <b>POWERFUL COMMANDS LIST</b> 📖
╚═══════════════════════════════════════════╝

<b>👑 Fᴏᴜɴᴅᴇʀ & Cᴏ-Fᴏᴜɴᴅᴇʀ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /cofounder @user - Aᴅᴅ Cᴏ-Fᴏᴜɴᴅᴇʀ
╰┈➤ /uncofounder @user - Rᴇᴍᴏᴠᴇ Cᴏ-Fᴏᴜɴᴅᴇʀ
╰┈➤ /mod @user - Aᴅᴅ Mᴏᴅᴇʀᴀᴛᴏʀ
╰┈➤ /unmod @user - Rᴇᴍᴏᴠᴇ Mᴏᴅᴇʀᴀᴛᴏʀ
╰┈➤ /muter @user - Aᴅᴅ Mᴜᴛᴇʀ
╰┈➤ /unmuter @user - Rᴇᴍᴏᴠᴇ Mᴜᴛᴇʀ
╰┈➤ /cleaner @user - Aᴅᴅ Cʜᴀᴛ Cʟᴇᴀɴᴇʀ
╰┈➤ /uncleaner @user - Rᴇᴍᴏᴠᴇ Cʜᴀᴛ Cʟᴇᴀɴᴇʀ
╰┈➤ /helper @user - Aᴅᴅ Hᴇʟᴘᴇʀ
╰┈➤ /unhelper @user - Rᴇᴍᴏᴠᴇ Hᴇʟᴘᴇʀ
╰┈➤ /free @user - Aᴅᴅ Fʀᴇᴇ Uꜱᴇʀ
╰┈➤ /unfree @user - Rᴇᴍᴏᴠᴇ Fʀᴇᴇ Uꜱᴇʀ

<b>👮 Aᴅᴍɪɴ & Mᴏᴅᴇʀᴀᴛᴏʀ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /reload - Rᴇʟᴏᴀᴅ ᴀᴅᴍɪɴs ʟɪsᴛ
╰┈➤ /settings - Mᴀɴᴀɢᴇ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs
╰┈➤ /ban @user - Bᴀɴ ᴜsᴇʀ
╰┈➤ /unban @user - Uɴʙᴀɴ ᴜsᴇʀ
╰┈➤ /kick @user - Kɪᴄᴋ ᴜsᴇʀ
╰┈➤ /mute @user - Mᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /unmute @user - Uɴᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /warn @user - Wᴀʀɴ ᴜsᴇʀ
╰┈➤ /unwarn @user - Rᴇᴍᴏᴠᴇ ᴡᴀʀɴ
╰┈➤ /warns @user - Cʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /delwarn - Dᴇʟᴇᴛᴇ & ᴡᴀʀɴ
╰┈➤ /resetwarns @user - Rᴇsᴇᴛ ᴀʟʟ ᴡᴀʀɴs

<b>📌 Pɪɴ Mᴇssᴀɢᴇs:</b>
╰┈➤ /pin - Pɪɴ ᴀ ᴍᴇssᴀɢᴇ
╰┈➤ /unpin - Uɴᴘɪɴ
╰┈➤ /pinned - Vɪᴇᴡ ᴘɪɴɴᴇᴅ
╰┈➤ /editpin - Eᴅɪᴛ ᴘɪɴɴᴇᴅ
╰┈➤ /delpin - Dᴇʟᴇᴛᴇ ᴘɪɴɴᴇᴅ

<b>🗑️ Dᴇʟᴇᴛᴇ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /del - Dᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ
╰┈➤ /logdel - Dᴇʟᴇᴛᴇ & ʟᴏɢ
╰┈➤ /purge - Pᴜʀɢᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴍᴇssᴀɢᴇs

<b>📊 Gᴇɴᴇʀᴀʟ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /start - Sᴛᴀʀᴛ ʙᴏᴛ
╰┈➤ /help - Gᴇᴛ ʜᴇʟᴘ
╰┈➤ /about - Aʙᴏᴜᴛ ʙᴏᴛ
╰┈➤ /ping - Cʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛs
╰┈➤ /staff - Vɪᴇᴡ sᴛᴀғғ ʟɪsᴛ
╰┈➤ /info @user - Gᴇᴛ ᴜsᴇʀ ɪɴғᴏ
╰┈➤ /infopvt @user - Iɴғᴏ ɪɴ ᴘʀɪᴠᴀᴛᴇ
╰┈➤ /me - Yᴏᴜʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
╰┈➤ /geturl - Gᴇᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ
╰┈➤ /sg @user - Uꜱᴇʀ ʜɪsᴛᴏʀʏ
╰┈➤ /history @user - Fᴜʟʟ ʜɪsᴛᴏʀʏ
╰┈➤ /chat - Cʜᴀᴛ ᴡɪᴛʜ ʙᴏᴛ
╰┈➤ /filter - Aᴅᴅ ғɪʟᴛᴇʀ
╰┈➤ /filters - Lɪsᴛ ғɪʟᴛᴇʀs

<b>🔰 Mᴏᴅᴇʀᴀᴛᴏʀ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /reload - Rᴇʟᴏᴀᴅ ᴀᴅᴍɪɴs
╰┈➤ /kick - Kɪᴄᴋ ᴜsᴇʀ
╰┈➤ /mute - Mᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /warn - Wᴀʀɴ ᴜsᴇʀ

<b>🔗 Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ:</b>
╰┈➤ Cʟɪᴄᴋ "Kɪᴅɴᴀᴘ Mᴇ" ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ

{self.get_owner_credit()}
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")],
            [InlineKeyboardButton("🔗 Kɪᴅɴᴀᴘ Mᴇ - Aᴅᴅ Tᴏ Gʀᴏᴜᴘ", url=f"https://t.me/{context.bot.username}?startgroup=start")]
        ]
        await update.message.reply_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ ABOUT COMMAND ─═◈═────
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        about_text = f"""
⚡ <b>Aʙᴏᴜᴛ {Config.BOT_NAME}</b> ⚡

────═◈═─ ✧◈✧ ─═◈═────
🤖 <b>Nᴀᴍᴇ:</b> {Config.BOT_NAME}  
📌 <b>ID:</b> {Config.BOT_USERNAME} 
👑 <b>Oᴡɴᴇʀ:</b> {Config.OWNER_NAME} 
📞 <b>Cᴏɴᴛᴀᴄᴛ:</b> {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 <b>Dᴇsᴄʀɪᴘᴛɪᴏɴ:</b>
Tʜᴇ Uʟᴛɪᴍᴀᴛᴇ Gʀᴏᴜᴘ Pʀᴏᴛᴇᴄᴛɪᴏɴ Bᴏᴛ

⚙️ <b>Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ Aɴᴛɪ-Sᴘᴀᴍ
╰┈➤ Aɴᴛɪ-Lɪɴᴋ
╰┈➤ Aɴᴛɪ-18+
╰┈➤ Wᴀʀɴ Sʏsᴛᴇᴍ
╰┈➤ Mᴜᴛᴇ/Uɴᴍᴜᴛᴇ
╰┈➤ Bᴀɴ/Kɪᴄᴋ
╰┈➤ Pɪɴ/Uɴᴘɪɴ
╰┈➤ Dᴇʟᴇᴛᴇ/Pᴜʀɢᴇ
╰┈➤ Fɪʟᴛᴇʀs
╰┈➤ SG (Uꜱᴇʀ Hɪsᴛᴏʀʏ)
╰┈➤ Rᴏʟᴇs Sʏsᴛᴇᴍ
╰┈➤ Sᴍᴀʀᴛ Cʜᴀᴛ

📢 <b>Vᴇʀsɪᴏɴ:</b> 3.0.0
🔰 <b>Sᴛᴀᴛᴜs:</b> Aᴄᴛɪᴠᴇ

{self.get_owner_credit()}
"""
        keyboard = [
            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")],
            [InlineKeyboardButton("🔗 Kɪᴅɴᴀᴘ Mᴇ - Aᴅᴅ Tᴏ Gʀᴏᴜᴘ", url=f"https://t.me/{context.bot.username}?startgroup=start")]
        ]
        await update.message.reply_text(about_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ STAFF COMMAND ─═◈═────
    async def staff_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        try:
            staff_members = await db.get_all_staff(chat.id)
            
            if not staff_members:
                await update.message.reply_text("👥 Nᴏ sᴛᴀғғ ᴍᴇᴍʙᴇʀs ғᴏᴜɴᴅ!", parse_mode="HTML")
                return
            
            staff_text = f"""
👥 <b>Sᴛᴀғғ Lɪsᴛ</b> 👥

────═◈═─ ✧◈✧ ─═◈═────
"""
            roles = {}
            for member in staff_members:
                role = member.get('role', 'Member')
                if role not in roles:
                    roles[role] = []
                roles[role].append(member)
            
            role_emojis = {
                'Founder': '👑',
                'Co-Founder': '⚜️',
                'Admin': '👔',
                'Moderator': '👷',
                'Muter': '🙊',
                'Chat Cleaner': '🛃',
                'Helper': '⛑',
                'Free': '🔓'
            }
            
            for role, members in roles.items():
                emoji = role_emojis.get(role, '👤')
                staff_text += f"\n{emoji} <b>{role}s ({len(members)})</b>\n"
                for member in members[:20]:
                    name = member.get('first_name', 'Unknown')
                    user_id = member.get('user_id', '')
                    staff_text += f"╰┈➤ {name} (<code>{user_id}</code>)\n"
                if len(members) > 20:
                    staff_text += f"╰┈➤ ... ᴀɴᴅ {len(members) - 20} ᴍᴏʀᴇ\n"
            
            staff_text += self.get_owner_credit()
            
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            await update.message.reply_text(staff_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ INFO COMMAND ─═◈═────
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        if not target:
            await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        try:
            chat = update.effective_chat
            user_full = await context.bot.get_chat(target.id)
            bio = getattr(user_full, 'bio', 'Nᴏ ʙɪᴏ sᴇᴛ')
            history_count = len(await db.get_user_history(target.id))
            msg_count = await db.get_user_message_count(target.id)
            role = await self.get_user_role(target.id, chat.id)
            
            info_text = f"""
📋 <b>Uꜱᴇʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Nᴀᴍᴇ:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{target.username if target.username else 'Nᴏɴᴇ'}
📝 <b>Bɪᴏ:</b> {bio[:100] if bio != 'Nᴏ ʙɪᴏ sᴇᴛ' else 'Nᴏ ʙɪᴏ sᴇᴛ'}
👑 <b>Rᴏʟᴇ:</b> {role}
📊 <b>Mᴇssᴀɢᴇs:</b> {msg_count}
🔄 <b>Nᴀᴍᴇ Cʜᴀɴɢᴇs:</b> {history_count}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
            
            keyboard = [
                [InlineKeyboardButton("👑 Rᴏʟᴇs", callback_data=f"role_menu_{target.id}")],
                [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
            ]
            
            await update.message.reply_text(info_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ ROLES MENU ─═◈═────
    async def roles_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        
        user_role = await self.get_user_role(user.id, chat.id)
        allowed_roles = ['Founder', 'Co-Founder']
        
        if user_role not in allowed_roles and user.id != Config.OWNER_ID:
            await update.message.reply_text("❌ Oɴʟʏ Fᴏᴜɴᴅᴇʀ ᴀɴᴅ Cᴏ-Fᴏᴜɴᴅᴇʀ ᴄᴀɴ ᴠɪᴇᴡ ᴛʜɪs ᴍᴇɴᴜ!")
            return
        
        roles_text = f"""
👑 <b>Uꜱᴇʀ Rᴏʟᴇs</b>

Uꜱᴇ ᴛʜᴇ ɪɴʟɪɴᴇ ᴋᴇʏʙᴏᴀʀᴅ ᴛᴏ ᴅɪsᴄᴏᴠᴇʀ ᴛʜᴇ ᴘᴏᴡᴇʀ ᴏғ ᴛʜᴇsᴇ ʀᴏʟᴇs!

<b>👑 Fᴏᴜɴᴅᴇʀ</b> - Gʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ, ᴀʟʟ ᴘᴏᴡᴇʀ
<b>⚜️ Cᴏ-Fᴏᴜɴᴅᴇʀ</b> - Aᴅᴍɪɴ ᴡɪᴛʜ ᴇxᴛʀᴀ ᴘᴏᴡᴇʀ
<b>👔 Aᴅᴍɪɴ</b> - Gʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ
<b>👷 Mᴏᴅᴇʀᴀᴛᴏʀ</b> - Cᴀɴ ᴍᴏᴅᴇʀᴀᴛᴇ ᴜsᴇʀs
<b>🙊 Mᴜᴛᴇʀ</b> - Cᴀɴ ᴍᴜᴛᴇ ᴜsᴇʀs
<b>🛃 Cʜᴀᴛ Cʟᴇᴀɴᴇʀ</b> - Cᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs
<b>⛑ Hᴇʟᴘᴇʀ</b> - Sᴛᴀғғ ʟɪsᴛ ᴏɴʟʏ
<b>🔓 Fʀᴇᴇ</b> - Iɢɴᴏʀᴇᴅ ʙʏ ᴀᴜᴛᴏ-ᴘᴜɴɪsʜᴍᴇɴᴛ

Tᴏ ᴀᴅᴅ/ʀᴇᴍᴏᴠᴇ ʀᴏʟᴇs:
/cᴏғᴏᴜɴᴅᴇʀ, /ᴍᴏᴅ, /ᴍᴜᴛᴇʀ, /ᴄʟᴇᴀɴᴇʀ, /ʜᴇʟᴘᴇʀ, /ғʀᴇᴇ
{self.get_owner_credit()}
"""
        keyboard = [
            [InlineKeyboardButton("👑 Fᴏᴜɴᴅᴇʀ", callback_data="role_founder")],
            [InlineKeyboardButton("⚜️ Cᴏ-Fᴏᴜɴᴅᴇʀ", callback_data="role_cofounder")],
            [InlineKeyboardButton("👔 Aᴅᴍɪɴ", callback_data="role_admin")],
            [InlineKeyboardButton("👷 Mᴏᴅᴇʀᴀᴛᴏʀ", callback_data="role_moderator")],
            [InlineKeyboardButton("🙊 Mᴜᴛᴇʀ", callback_data="role_muter")],
            [InlineKeyboardButton("🛃 Cʜᴀᴛ Cʟᴇᴀɴᴇʀ", callback_data="role_cleaner")],
            [InlineKeyboardButton("⛑ Hᴇʟᴘᴇʀ", callback_data="role_helper")],
            [InlineKeyboardButton("🔓 Fʀᴇᴇ", callback_data="role_free")],
            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
        ]
        await update.message.reply_text(roles_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ CALLBACK HANDLER ─═◈═────
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
        
        if data == "main_menu":
            user = update.effective_user
            main_text = await self.get_main_menu_message(user, is_premium)
            
            keyboard = [
                [InlineKeyboardButton("📊 Sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ Sᴇᴛᴛɪɴɢs", callback_data="settings")],
                [InlineKeyboardButton("📖 Hᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ Aʙᴏᴜᴛ", callback_data="about")],
                [InlineKeyboardButton("👥 Sᴛᴀғғ", callback_data="staff"), InlineKeyboardButton("🔄 SG", callback_data="sg")],
                [InlineKeyboardButton("📜 Hɪsᴛᴏʀʏ", callback_data="history"), InlineKeyboardButton("💬 Cʜᴀᴛ", callback_data="chat")],
                [InlineKeyboardButton("👑 Rᴏʟᴇs", callback_data="roles")],
                [InlineKeyboardButton("🔗 Kɪᴅɴᴀᴘ Mᴇ - Aᴅᴅ Tᴏ Gʀᴏᴜᴘ", url=f"https://t.me/{context.bot.username}?startgroup=start")]
            ]
            if is_premium:
                keyboard.append([InlineKeyboardButton("💎 Pʀᴇᴍɪᴜᴍ", callback_data="premium")])
            
            try:
                await query.edit_message_text(
                    main_text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
        
        elif data == "help":
            help_text = f"""
📖 <b>POWERFUL COMMANDS LIST</b> 📖

<b>👑 Fᴏᴜɴᴅᴇʀ & Cᴏ-Fᴏᴜɴᴅᴇʀ:</b>
/cᴏғᴏᴜɴᴅᴇʀ, /ᴜɴᴄᴏғᴏᴜɴᴅᴇʀ
/ᴍᴏᴅ, /ᴜɴᴍᴏᴅ
/ᴍᴜᴛᴇʀ, /ᴜɴᴍᴜᴛᴇʀ
/ᴄʟᴇᴀɴᴇʀ, /ᴜɴᴄʟᴇᴀɴᴇʀ
/ʜᴇʟᴘᴇʀ, /ᴜɴʜᴇʟᴘᴇʀ
/ғʀᴇᴇ, /ᴜɴғʀᴇᴇ

<b>👮 Aᴅᴍɪɴ & Mᴏᴅᴇʀᴀᴛᴏʀ:</b>
/ʀᴇʟᴏᴀᴅ, /sᴇᴛᴛɪɴɢs
/ʙᴀɴ, /ᴜɴʙᴀɴ, /ᴋɪᴄᴋ
/ᴍᴜᴛᴇ, /ᴜɴᴍᴜᴛᴇ
/ᴡᴀʀɴ, /ᴜɴᴡᴀʀɴ, /ᴡᴀʀɴs

<b>📌 Pɪɴ Mᴇssᴀɢᴇs:</b>
/ᴘɪɴ, /ᴜɴᴘɪɴ, /ᴘɪɴɴᴇᴅ
/ᴇᴅɪᴛᴘɪɴ, /ᴅᴇʟᴘɪɴ

<b>🗑️ Dᴇʟᴇᴛᴇ:</b>
/ᴅᴇʟ, /ʟᴏɢᴅᴇʟ, /ᴘᴜʀɢᴇ

<b>📊 Gᴇɴᴇʀᴀʟ:</b>
/sᴛᴀʀᴛ, /ʜᴇʟᴘ, /ᴀʙᴏᴜᴛ
/ᴘɪɴɢ, /sᴛᴀғғ
/ɪɴꜰᴏ, /ɪɴꜰᴏᴘᴠᴛ, /ᴍᴇ
/ɢᴇᴛᴜʀʟ, /sɢ, /ʜɪsᴛᴏʀʏ
/ᴄʜᴀᴛ, /ғɪʟᴛᴇʀ, /ғɪʟᴛᴇʀs

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass
        
        elif data == "about":
            text = f"""
⚡ <b>Aʙᴏᴜᴛ {Config.BOT_NAME}</b> ⚡

────═◈═─ ✧◈✧ ─═◈═────
🤖 <b>Nᴀᴍᴇ:</b> {Config.BOT_NAME}  
📌 <b>ID:</b> {Config.BOT_USERNAME} 
👑 <b>Oᴡɴᴇʀ:</b> {Config.OWNER_NAME} 
📞 <b>Cᴏɴᴛᴀᴄᴛ:</b> {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 <b>Dᴇsᴄʀɪᴘᴛɪᴏɴ:</b>
Tʜᴇ Uʟᴛɪᴍᴀᴛᴇ Gʀᴏᴜᴘ Mᴀɴᴀɢᴇᴍᴇɴᴛ Bᴏᴛ

📢 <b>Vᴇʀsɪᴏɴ:</b> 3.0.0
🔰 <b>Sᴛᴀᴛᴜs:</b> Aᴄᴛɪᴠᴇ

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass
        
        elif data == "staff":
            await query.edit_message_text("👥 Uꜱᴇ /sᴛᴀғғ ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ!", parse_mode="HTML")
        
        elif data == "sg":
            await query.edit_message_text(
                f"🔄 <b>SG - Uꜱᴇʀ Hɪsᴛᴏʀʏ</b>\n\n"
                f"Uꜱᴇ /sɢ @ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ\n"
                f"Tᴏ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴄᴏᴍᴘʟᴇᴛᴇ ʜɪsᴛᴏʀʏ!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "history":
            await query.edit_message_text(
                f"📜 <b>Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ</b>\n\n"
                f"Uꜱᴇ /ʜɪsᴛᴏʀʏ @ᴜsᴇʀɴᴀᴍᴇ\n"
                f"Tᴏ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴄᴏᴍᴘʟᴇᴛᴇ ᴄʜᴀɴɢᴇ ʜɪsᴛᴏʀʏ!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "chat":
            await query.edit_message_text(
                f"💬 <b>Cʜᴀᴛ ᴡɪᴛʜ ᴍᴇ!</b>\n\n"
                f"Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴀɴᴅ I'ʟʟ ʀᴇsᴘᴏɴᴅ!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "roles":
            roles_text = f"""
👑 <b>Uꜱᴇʀ Rᴏʟᴇs</b>

<b>👑 Fᴏᴜɴᴅᴇʀ</b> - Gʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ, ᴀʟʟ ᴘᴏᴡᴇʀ
<b>⚜️ Cᴏ-Fᴏᴜɴᴅᴇʀ</b> - Aᴅᴍɪɴ ᴡɪᴛʜ ᴇxᴛʀᴀ ᴘᴏᴡᴇʀ
<b>👔 Aᴅᴍɪɴ</b> - Gʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ
<b>👷 Mᴏᴅᴇʀᴀᴛᴏʀ</b> - Cᴀɴ ᴍᴏᴅᴇʀᴀᴛᴇ ᴜsᴇʀs
<b>🙊 Mᴜᴛᴇʀ</b> - Cᴀɴ ᴍᴜᴛᴇ ᴜsᴇʀs
<b>🛃 Cʜᴀᴛ Cʟᴇᴀɴᴇʀ</b> - Cᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs
<b>⛑ Hᴇʟᴘᴇʀ</b> - Sᴛᴀғғ ʟɪsᴛ ᴏɴʟʏ
<b>🔓 Fʀᴇᴇ</b> - Iɢɴᴏʀᴇᴅ ʙʏ ᴀᴜᴛᴏ-ᴘᴜɴɪsʜᴍᴇɴᴛ

Tᴏ ᴀᴅᴅ/ʀᴇᴍᴏᴠᴇ ʀᴏʟᴇs:
/cᴏғᴏᴜɴᴅᴇʀ, /ᴍᴏᴅ, /ᴍᴜᴛᴇʀ, /ᴄʟᴇᴀɴᴇʀ, /ʜᴇʟᴘᴇʀ, /ғʀᴇᴇ
{self.get_owner_credit()}
"""
            keyboard = [
                [InlineKeyboardButton("👑 Fᴏᴜɴᴅᴇʀ", callback_data="role_founder")],
                [InlineKeyboardButton("⚜️ Cᴏ-Fᴏᴜɴᴅᴇʀ", callback_data="role_cofounder")],
                [InlineKeyboardButton("👔 Aᴅᴍɪɴ", callback_data="role_admin")],
                [InlineKeyboardButton("👷 Mᴏᴅᴇʀᴀᴛᴏʀ", callback_data="role_moderator")],
                [InlineKeyboardButton("🙊 Mᴜᴛᴇʀ", callback_data="role_muter")],
                [InlineKeyboardButton("🛃 Cʜᴀᴛ Cʟᴇᴀɴᴇʀ", callback_data="role_cleaner")],
                [InlineKeyboardButton("⛑ Hᴇʟᴘᴇʀ", callback_data="role_helper")],
                [InlineKeyboardButton("🔓 Fʀᴇᴇ", callback_data="role_free")],
                [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(roles_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass
        
        elif data.startswith("role_"):
            role_name = data.replace("role_", "").upper()
            await query.edit_message_text(
                f"👑 <b>{role_name} Rᴏʟᴇ</b>\n\n"
                f"Tᴏ ᴀᴅᴅ ᴛʜɪs ʀᴏʟᴇ: /{role_name.lower()} @ᴜsᴇʀ\n"
                f"Tᴏ ʀᴇᴍᴏᴠᴇ ᴛʜɪs ʀᴏʟᴇ: /ᴜɴ{role_name.lower()} @ᴜsᴇʀ\n\n"
                f"<b>Dᴇsᴄʀɪᴘᴛɪᴏɴ:</b>\n"
                f"{self.get_role_description(role_name)}{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("👋 Wᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 Gᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ Aɴᴛɪ-Sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 Aɴᴛɪ-Lɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 Aɴᴛɪ-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(
                    f"⚙️ <b>Sᴇᴛᴛɪɴɢs Mᴇɴᴜ</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                pass
        
        elif data.startswith("set_"):
            setting = data.replace("set_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            try:
                await query.edit_message_text(
                    f"✅ <b>{setting.upper()}</b> {'Enabled' if not current else 'Disabled'}!{self.get_owner_credit()}",
                    parse_mode="HTML"
                )
            except:
                pass
        
        elif data == "stats":
            if user_id != Config.OWNER_ID:
                await query.edit_message_text("❌ Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!", parse_mode="HTML")
                return
            
            users_count = db.users.count_documents({})
            groups_count = db.groups.count_documents({})
            warnings_count = db.warnings.count_documents({})
            mutes_count = db.mutes.count_documents({})
            
            text = f"""
📊 <b>Bᴏᴛ Sᴛᴀᴛɪsᴛɪᴄs</b> 📊

────═◈═─ ✧◈✧ ─═◈═────
👥 Tᴏᴛᴀʟ Uꜱᴇʀs: {users_count}  
📍 Tᴏᴛᴀʟ Gʀᴏᴜᴘs: {groups_count} 
⚠️ Wᴀʀɴɪɴɢs: {warnings_count}   
🔇 Aᴄᴛɪᴠᴇ Mᴜᴛᴇs: {mutes_count} 
────═◈═─ ✧◈✧ ─═◈═────
🔥 <b>Bᴏᴛ Iɴғᴏ:</b>
╰┈➤ Nᴀᴍᴇ: {Config.BOT_NAME}
╰┈➤ Vᴇʀsɪᴏɴ: 3.0.0
╰┈➤ Oᴡɴᴇʀ: {Config.OWNER_NAME}
⚡ <b>Sᴛᴀᴛᴜs:</b> Oɴʟɪɴᴇ

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass
        
        elif data == "premium":
            if is_premium:
                text = f"""
💎 <b>Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs</b> 💎
✅ <b>Yᴏᴜ ᴀʀᴇ ᴀ Pʀᴇᴍɪᴜᴍ Uꜱᴇʀ!</b>

<b>Uɴʟᴏᴄᴋᴇᴅ Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ Aɴᴛɪ-Cʀᴀsʜ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴛɪ-Sᴘᴀᴍ
╰┈➤ Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ GɪF
╰┈➤ Pʀɪᴠᴀᴛᴇ Lᴏɢs
╰┈➤ 24/7 Sᴜᴘᴘᴏʀᴛ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴀʟʏᴛɪᴄs
╰┈➤ Cᴜsᴛᴏᴍ Cᴏᴍᴍᴀɴᴅs

{self.get_owner_credit()}
"""
            else:
                text = f"""
💎 <b>Pʀᴇᴍɪᴜᴍ Pʟᴀɴ</b> 💎

<b>Uɴʟᴏᴄᴋ Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ Aɴᴛɪ-Cʀᴀsʜ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴛɪ-Sᴘᴀᴍ
╰┈➤ Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ GɪF
╰┈➤ Pʀɪᴠᴀᴛᴇ Lᴏɢs
╰┈➤ 24/7 Sᴜᴘᴘᴏʀᴛ
╰┈➤ Aᴅᴠᴀɴᴄᴇᴅ Aɴᴀʟʏᴛɪᴄs
╰┈➤ Cᴜsᴛᴏᴍ Cᴏᴍᴍᴀɴᴅs

<b>Pʀɪᴄᴇ:</b> $5/ᴍᴏɴᴛʜ

Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ Tᴏ Bᴜʏ:
📞 {Config.OWNER_USERNAME}

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                pass

    def get_role_description(self, role_name):
        descriptions = {
            "FOUNDER": "Gʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ᴡɪᴛʜ ᴀʟʟ ᴘᴏᴡᴇʀs",
            "CO-FOUNDER": "Aᴅᴍɪɴ ᴡɪᴛʜ ᴇxᴛʀᴀ ᴘᴏᴡᴇʀ ᴛᴏ ᴍᴀɴᴀɢᴇ sᴛᴀғғ",
            "ADMIN": "Gʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ",
            "MODERATOR": "Cᴀɴ ᴍᴏᴅᴇʀᴀᴛᴇ ᴜsᴇʀs ᴡɪᴛʜ ᴄᴏᴍᴍᴀɴᴅs",
            "MUTER": "Cᴀɴ ᴍᴜᴛᴇ ᴀɴᴅ ᴜɴᴍᴜᴛᴇ ᴜsᴇʀs",
            "CLEANER": "Cᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs",
            "HELPER": "Aᴘᴘᴇᴀʀs ɪɴ sᴛᴀғғ ʟɪsᴛ",
            "FREE": "Iɢɴᴏʀᴇᴅ ʙʏ ᴀᴜᴛᴏᴍᴀᴛɪᴄ ᴘᴜɴɪsʜᴍᴇɴᴛ"
        }
        return descriptions.get(role_name, "")

    # ────═◈═─ ERROR HANDLER ─═◈═────
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"❌ <b>Error occurred!</b>\n<code>{str(context.error)[:100]}</code>{self.get_owner_credit()}",
                    parse_mode="HTML"
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
            self.app.add_handler(CommandHandler("ping", self.ping_command))
            self.app.add_handler(CommandHandler("staff", self.staff_command))
            self.app.add_handler(CommandHandler("stats", self.stats_command))
            self.app.add_handler(CommandHandler("setrules", self.set_rules))
            self.app.add_handler(CommandHandler("rules", self.get_rules))
            self.app.add_handler(CommandHandler("settings", self.settings_command))
            self.app.add_handler(CommandHandler("reload", self.reload_command))
            self.app.add_handler(CommandHandler("info", self.info_command))
            self.app.add_handler(CommandHandler("infopvt", self.infopvt_command))
            self.app.add_handler(CommandHandler("me", self.me_command))
            self.app.add_handler(CommandHandler("geturl", self.geturl_command))
            self.app.add_handler(CommandHandler("pinned", self.pinned_command))
            self.app.add_handler(CommandHandler("filter", self.add_filter))
            self.app.add_handler(CommandHandler("stopfilter", self.remove_filter))
            self.app.add_handler(CommandHandler("filters", self.list_filters))
            self.app.add_handler(CommandHandler("enablewelcome", self.enable_welcome))
            self.app.add_handler(CommandHandler("disablewelcome", self.disable_welcome))
            self.app.add_handler(CommandHandler("sg", self.sg_command))
            self.app.add_handler(CommandHandler("history", self.history_command))
            self.app.add_handler(CommandHandler("chat", self.chat_command))
            self.app.add_handler(CommandHandler("roles", self.roles_menu))
            
            # Role management commands
            self.app.add_handler(CommandHandler("cofounder", self.cofounder_command))
            self.app.add_handler(CommandHandler("uncofounder", self.uncofounder_command))
            self.app.add_handler(CommandHandler("mod", self.moderator_command))
            self.app.add_handler(CommandHandler("unmod", self.unmoderator_command))
            self.app.add_handler(CommandHandler("muter", self.muter_command))
            self.app.add_handler(CommandHandler("unmuter", self.unmuter_command))
            self.app.add_handler(CommandHandler("cleaner", self.cleaner_command))
            self.app.add_handler(CommandHandler("uncleaner", self.uncleaner_command))
            self.app.add_handler(CommandHandler("helper", self.helper_command))
            self.app.add_handler(CommandHandler("unhelper", self.unhelper_command))
            self.app.add_handler(CommandHandler("free", self.free_command))
            self.app.add_handler(CommandHandler("unfree", self.unfree_command))
            
            # Moderation commands
            self.app.add_handler(CommandHandler("warn", self.warn_command))
            self.app.add_handler(CommandHandler("unwarn", self.unwarn_command))
            self.app.add_handler(CommandHandler("warns", self.warns_command))
            self.app.add_handler(CommandHandler("delwarn", self.delwarn_command))
            self.app.add_handler(CommandHandler("resetwarns", self.reset_warns))
            self.app.add_handler(CommandHandler("mute", self.mute_command))
            self.app.add_handler(CommandHandler("unmute", self.unmute_command))
            self.app.add_handler(CommandHandler("kick", self.kick_command))
            self.app.add_handler(CommandHandler("ban", self.ban_command))
            self.app.add_handler(CommandHandler("unban", self.unban_command))
            self.app.add_handler(CommandHandler("pin", self.pin_command))
            self.app.add_handler(CommandHandler("unpin", self.unpin_command))
            self.app.add_handler(CommandHandler("del", self.del_command))
            self.app.add_handler(CommandHandler("logdel", self.logdel_command))
            self.app.add_handler(CommandHandler("purge", self.purge_command))
            self.app.add_handler(CommandHandler("approve", self.approve_command))
            self.app.add_handler(CommandHandler("unapprove", self.unapprove_command))
            
            # Callback handler
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            
            # Message handlers
            self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome_handler))
            self.app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, self.goodbye_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.antispam_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.antilink_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.anti18_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.filter_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.smart_chat_handler))
            
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
