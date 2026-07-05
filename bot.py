#!/usr/bin/env python3
"""
ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ - ᴘʀᴇᴍɪᴜᴍ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ
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
from database import Database

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

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
        self.log_channel = Config.LOG_CHANNEL
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

    async def is_mod(self, context, chat_id, user_id):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except:
            return False

    async def get_user_info(self, context, user_id):
        try:
            user = await context.bot.get_chat(user_id)
            return user
        except:
            return None

    async def log_action(self, chat_id, message):
        if self.log_channel:
            try:
                await self.app.bot.send_message(self.log_channel, message, parse_mode="Markdown")
            except:
                pass

    def get_footer(self):
        return f"\n\n:⧽ ʙʏ » {Config.OWNER_NAME}"

    # ────═◈═─ START COMMAND ─═◈═────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.add_user(user.id, user.username, user.first_name)
        
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        welcome_text = f"""
⚡ **ᴘɪᴋᴀᴄʜᴜ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ** ⚡

✨ **ʜᴇʟʟᴏ {user.first_name}!** ✨

ɪ ᴀᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ!

**🔰 ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ 🛡️ Aɴᴛɪ-sᴘᴀᴍ & Lɪɴᴋ Sʜɪᴇʟᴅ
╰┈➤ ⚠️ Wᴀʀɴ/Mᴜᴛᴇ/Bᴀɴ/Kɪᴄᴋ
╰┈➤ 📌 Pɪɴ/Uɴᴘɪɴ/Dᴇʟᴇᴛᴇ/Pᴜʀɢᴇ
╰┈➤ 👋 Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ
╰┈➤ 📊 Sᴛᴀғғ Lɪsᴛ & Sᴛᴀᴛs
╰┈➤ 📋 Cᴜsᴛᴏᴍ Rᴜʟᴇs
╰┈➤ 💎 Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs

💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs:** {'✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}

📌 **ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!**
{self.get_footer()}
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")],
            [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
            [InlineKeyboardButton("👥 sᴛᴀғғ", callback_data="staff")]
        ]
        if is_premium:
            keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
        
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ HELP COMMAND ─═◈═────
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

╔═══════════════════════════════════════╗

**👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**

╰┈➤ /warn @user - ᴡᴀʀɴ ᴜsᴇʀ
╰┈➤ /unwarn @user - ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴ
╰┈➤ /warns @user - ᴄʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /delwarn - ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ & ᴡᴀʀɴ ᴜsᴇʀ
╰┈➤ /resetwarns @user - ʀᴇsᴇᴛ ᴀʟʟ ᴡᴀʀɴs
╰┈➤ /mute @user - ᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /unmute @user - ᴜɴᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /kick @user - ᴋɪᴄᴋ ᴜsᴇʀ
╰┈➤ /ban @user - ʙᴀɴ ᴜsᴇʀ
╰┈➤ /unban @user - ᴜɴʙᴀɴ ᴜsᴇʀ
╰┈➤ /pin - ᴘɪɴ ᴀ ᴍᴇssᴀɢᴇ (ʀᴇᴘʟʏ)
╰┈➤ /unpin - ᴜɴᴘɪɴ ᴄᴜʀʀᴇɴᴛ ᴘɪɴ
╰┈➤ /del - ᴅᴇʟᴇᴛᴇ ᴀ ᴍᴇssᴀɢᴇ (ʀᴇᴘʟʏ)
╰┈➤ /logdel - ᴅᴇʟᴇᴛᴇ & ʟᴏɢ ᴍᴇssᴀɢᴇ
╰┈➤ /purge - ᴄʟᴇᴀʀ ᴍᴜʟᴛɪᴘʟᴇ ᴍᴇssᴀɢᴇs
╰┈➤ /reload - ʀᴇғʀᴇsʜ ᴀᴅᴍɪɴs ʟɪsᴛ
╰┈➤ /settings - ᴍᴀɴᴀɢᴇ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs
╰┈➤ /rules - ᴠɪᴇᴡ ɢʀᴏᴜᴘ ʀᴜʟᴇs
╰┈➤ /setrules - sᴇᴛ ɢʀᴏᴜᴘ ʀᴜʟᴇs
╰┈➤ /approve @user - ᴀᴘᴘʀᴏᴠᴇ ᴜsᴇʀ
╰┈➤ /unapprove @user - ʀᴇᴠᴏᴋᴇ ᴀᴘᴘʀᴏᴠᴀʟ

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**

╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ
╰┈➤ /ping - ᴄʜᴇᴄᴋ ʙᴏᴛ & sʏsᴛᴇᴍ sᴛᴀᴛs
╰┈➤ /staff - ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ
╰┈➤ /info @user - ɢᴇᴛ ᴜsᴇʀ ɪɴғᴏ
╰┈➤ /infopvt @user - ɢᴇᴛ ᴜsᴇʀ ɪɴғᴏ ɪɴ ᴘʀɪᴠᴀᴛᴇ
╰┈➤ /me - ʏᴏᴜʀ ᴏᴡɴ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
╰┈➤ /pinned - ᴠɪᴇᴡ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ
╰┈➤ /geturl - ɢᴇᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ

**🔰 ᴍᴏᴅᴇʀᴀᴛᴏʀ ᴄᴏᴍᴍᴀɴᴅs:**

╰┈➤ /reload - ᴜᴘᴅᴀᴛᴇ ᴀᴅᴍɪɴs ʟɪsᴛ
╰┈➤ /kick - ᴋɪᴄᴋ ᴜsᴇʀ
╰┈➤ /mute - ᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /warn - ᴡᴀʀɴ ᴜsᴇʀ

╚═══════════════════════════════════════╝

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
{self.get_footer()}
"""
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ GET URL COMMAND ─═◈═────
    async def geturl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ɢᴇᴛ ɪᴛs ʟɪɴᴋ!")
            return
        
        chat = update.effective_chat
        msg = update.message.reply_to_message
        link = f"https://t.me/{chat.username}/{msg.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{msg.message_id}"
        await update.message.reply_text(f"🔗 **ᴍᴇssᴀɢᴇ ʟɪɴᴋ:**\n{link}\n{self.get_footer()}", parse_mode="Markdown")

    # ────═◈═─ INFO COMMAND ─═◈═────
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        if not target:
            await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        try:
            user_full = await context.bot.get_chat(target.id)
            bio = getattr(user_full, 'bio', 'N/A')
            status = "👑 Oᴡɴᴇʀ" if target.id == update.effective_chat.id else "👤 Mᴇᴍʙᴇʀ"
            
            info_text = f"""
📋 **ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**

────═◈═─ ✧◈✧ ─═◈═────
👤 **ɴᴀᴍᴇ:** {target.first_name}
🆔 **ɪᴅ:** `{target.id}`
📛 **ᴜsᴇʀɴᴀᴍᴇ:** @{target.username if target.username else 'N/A'}
📝 **ʙɪᴏ:** {bio[:100] if bio != 'N/A' else 'N/A'}
🔰 **sᴛᴀᴛᴜs:** {status}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_footer()}
"""
            await update.message.reply_text(info_text, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def infopvt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        if not target:
            await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        try:
            user_full = await context.bot.get_chat(target.id)
            bio = getattr(user_full, 'bio', 'N/A')
            
            info_text = f"""
📋 **ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**

────═◈═─ ✧◈✧ ─═◈═────
👤 **ɴᴀᴍᴇ:** {target.first_name}
🆔 **ɪᴅ:** `{target.id}`
📛 **ᴜsᴇʀɴᴀᴍᴇ:** @{target.username if target.username else 'N/A'}
📝 **ʙɪᴏ:** {bio[:100] if bio != 'N/A' else 'N/A'}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_footer()}
"""
            await context.bot.send_message(update.effective_user.id, info_text, parse_mode="Markdown")
            await update.message.reply_text(f"✅ **ɪɴғᴏʀᴍᴀᴛɪᴏɴ sᴇɴᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ!**\n{self.get_footer()}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ ME COMMAND ─═◈═────
    async def me_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        
        warnings = await db.get_warnings(user.id, chat.id)
        rules = await db.get_rules(chat.id)
        
        me_text = f"""
📋 **ʏᴏᴜʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**

────═◈═─ ✧◈✧ ─═◈═────
👤 **ɴᴀᴍᴇ:** {user.first_name}
🆔 **ɪᴅ:** `{user.id}`
📛 **ᴜsᴇʀɴᴀᴍᴇ:** @{user.username if user.username else 'N/A'}
⚠️ **ᴡᴀʀɴs:** {len(warnings)}
📋 **ʀᴜʟᴇs:** {rules[:100] if rules else 'N/A'}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_footer()}
"""
        await update.message.reply_text(me_text, parse_mode="Markdown")

    # ────═◈═─ PIN COMMANDS ─═◈═────
    async def pin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘɪɴ ᴍᴇssᴀɢᴇs!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ!")
            return
        
        try:
            await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
            await update.message.reply_text(f"📌 **ᴘɪɴɴᴇᴅ!**\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"📌 **ᴘɪɴɴᴇᴅ** ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def unpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs!")
            return
        
        try:
            await context.bot.unpin_chat_message(chat.id)
            await update.message.reply_text(f"📌 **ᴜɴᴘɪɴɴᴇᴅ!**\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"📌 **ᴜɴᴘɪɴɴᴇᴅ** ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def pinned_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        try:
            pinned = await context.bot.get_chat(chat.id)
            if pinned.pinned_message:
                link = f"https://t.me/{chat.username}/{pinned.pinned_message.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{pinned.pinned_message.message_id}"
                await update.message.reply_text(f"📌 **ᴄᴜʀʀᴇɴᴛ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ:**\n{link}\n{self.get_footer()}", parse_mode="Markdown")
            else:
                await update.message.reply_text(f"📌 **ɴᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!**\n{self.get_footer()}", parse_mode="Markdown")
        except:
            await update.message.reply_text(f"❌ ᴜɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!\n{self.get_footer()}", parse_mode="Markdown")

    # ────═◈═─ DELETE/PURGE COMMANDS ─═◈═────
    async def del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ!")
            return
        
        try:
            await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await self.log_action(chat.id, f"🗑️ **ᴅᴇʟᴇᴛᴇᴅ** ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def logdel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        msg = update.message.reply_to_message
        try:
            log_msg = f"""
🗑️ **ʟᴏɢ ᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ**

📝 **ᴄᴏɴᴛᴇɴᴛ:** {msg.text if msg.text else 'Mᴇᴅɪᴀ'}
👤 **ᴜsᴇʀ:** {msg.from_user.first_name}
🆔 **ɪᴅ:** `{msg.from_user.id}`
👮 **ʙʏ:** {user.first_name}
📍 **ɢʀᴏᴜᴘ:** {chat.title}
"""
            await self.log_action(chat.id, log_msg)
            await context.bot.delete_message(chat.id, msg.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(f"✅ **ᴅᴇʟᴇᴛᴇᴅ ᴀɴᴅ ʟᴏɢɢᴇᴅ!**\n{self.get_footer()}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def purge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘᴜʀɢᴇ ғʀᴏᴍ!")
            return
        
        try:
            msg_id = update.message.reply_to_message.message_id
            current_id = update.message.message_id
            deleted = 0
            
            for i in range(msg_id, current_id):
                try:
                    await context.bot.delete_message(chat.id, i)
                    deleted += 1
                    await asyncio.sleep(0.1)
                except:
                    pass
            
            await update.message.reply_text(f"🗑️ **ᴅᴇʟᴇᴛᴇᴅ {deleted} ᴍᴇssᴀɢᴇs!**\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"🗑️ **ᴘᴜʀɢᴇᴅ** {deleted} ᴍᴇssᴀɢᴇs ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ RELOAD COMMAND ─═◈═────
    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇʟᴏᴀᴅ!")
            return
        
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            await db.update_settings(chat.id, "admins", [admin.user.id for admin in admins])
            await update.message.reply_text(f"✅ **ᴀᴅᴍɪɴs ʟɪsᴛ ʀᴇʟᴏᴀᴅᴇᴅ!**\n{self.get_footer()}", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ STAFF COMMAND ─═◈═────
    async def staff_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            owner = None
            admin_list = []
            
            for admin in admins:
                if admin.status == 'creator':
                    owner = admin.user
                else:
                    admin_list.append(admin.user)
            
            staff_text = f"""
👥 **sᴛᴀғғ ʟɪsᴛ** 👥

────═◈═─ ✧◈✧ ─═◈═────
👑 **ᴏᴡɴᴇʀ:**
╰┈➤ {owner.first_name}

👔 **ᴀᴅᴍɪɴs: ({len(admin_list)})**
"""
            for admin in admin_list:
                staff_text += f"╰┈➤ {admin.first_name}\n"
            
            staff_text += f"\n📊 **ᴛᴏᴛᴀʟ sᴛᴀғғ:** {len(admin_list) + 1}"
            staff_text += self.get_footer()
            
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            await update.message.reply_text(staff_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ SETTINGS COMMAND ─═◈═────
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴠɪᴇᴡ sᴇᴛᴛɪɴɢs!")
            return
        
        settings = await db.get_settings(chat.id)
        
        keyboard = [
            [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
            [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
            [InlineKeyboardButton("🔞 ᴀɴᴛɪ-18+", callback_data="set_anti18"), InlineKeyboardButton("⚠️ ᴡᴀʀɴ ʟɪᴍɪᴛ", callback_data="set_warnlimit")],
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
        ]
        
        settings_text = f"""
⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**

📍 **ɢʀᴏᴜᴘ:** {chat.title}

**ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs:**
├ ᴀɴᴛɪ-sᴘᴀᴍ: {'✅' if settings.get('antispam', True) else '❌'}
├ ᴀɴᴛɪ-ʟɪɴᴋ: {'✅' if settings.get('antilink', False) else '❌'}
├ ᴀɴᴛɪ-18+: {'✅' if settings.get('anti18', True) else '❌'}
├ ᴡᴇʟᴄᴏᴍᴇ: {'✅' if settings.get('welcome', True) else '❌'}
├ ɢᴏᴏᴅʙʏᴇ: {'✅' if settings.get('goodbye', True) else '❌'}
└ ᴡᴀʀɴ ʟɪᴍɪᴛ: {settings.get('warn_limit', 3)}

sᴇʟᴇᴄᴛ ᴀ sᴇᴛᴛɪɴɢ ᴛᴏ ᴄʜᴀɴɢᴇ.
{self.get_footer()}
"""
        await update.message.reply_text(settings_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ RULES COMMANDS ─═◈═────
    async def set_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ʀᴜʟᴇs!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ʀᴜʟᴇs!\nᴇxᴀᴍᴘʟᴇ: `/setrules ɴᴏ sᴘᴀᴍ, ɴᴏ ᴀʙᴜsᴇ`")
            return
        
        rules = " ".join(context.args)
        await db.set_rules(chat.id, rules)
        await update.message.reply_text(f"✅ **ʀᴜʟᴇs sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n📋 {rules}\n{self.get_footer()}", parse_mode="Markdown")

    async def get_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        rules = await db.get_rules(chat.id)
        
        if rules:
            await update.message.reply_text(f"📋 **ɢʀᴏᴜᴘ ʀᴜʟᴇs:**\n\n{rules}\n{self.get_footer()}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"ℹ️ ɴᴏ ʀᴜʟᴇs sᴇᴛ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.\nᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ʀᴜʟᴇs ᴜsɪɴɢ `/setrules`\n{self.get_footer()}", parse_mode="Markdown")

    # ────═◈═─ PING COMMAND ─═◈═────
    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            # CPU Usage
            cpu_usage = psutil.cpu_percent(interval=0.5)
            
            # RAM Usage
            ram = psutil.virtual_memory()
            ram_used = ram.used / (1024 ** 3)
            ram_total = ram.total / (1024 ** 3)
            ram_percent = ram.percent
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_used = disk.used / (1024 ** 3)
            disk_total = disk.total / (1024 ** 3)
            disk_percent = disk.percent
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_str = str(uptime).split('.')[0]
        except:
            cpu_usage = "N/A"
            ram_used = "N/A"
            ram_total = "N/A"
            ram_percent = "N/A"
            disk_used = "N/A"
            disk_total = "N/A"
            disk_percent = "N/A"
            uptime_str = "N/A"
        
        start_time = datetime.now()
        msg = await update.message.reply_text("🏓 Pɪɴɢɪɴɢ...")
        end_time = datetime.now()
        latency = (end_time - start_time).microseconds / 1000
        
        ping_text = f"""
⚡️ **{Config.BOT_NAME}**

🏓 ᴘɪɴɢ..ᴩᴏɴɢ : `{latency:.3f}ᴍs`

» **sʏsᴛᴇᴍ sᴛᴀᴛs :**

:⧽ ᴜᴩᴛɪᴍᴇ : `{uptime_str}`
:⧽ ʀᴀᴍ : `{ram_used:.2f}GB / {ram_total:.2f}GB` ({ram_percent}%)
:⧽ ᴄᴩᴜ : `{cpu_usage}%`
:⧽ ᴅɪsᴋ : `{disk_used:.2f}GB / {disk_total:.2f}GB` ({disk_percent}%)
:⧽ ᴩʏ-ᴛɢᴄᴀʟʟs : `✅ ᴀᴄᴛɪᴠᴇ`

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        
        await msg.edit_text(ping_text, parse_mode="Markdown")

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
╰┈➤ ᴀɴᴛɪ-18+
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ
╰┈➤ ᴘɪɴ/ᴜɴᴘɪɴ
╰┈➤ ᴅᴇʟᴇᴛᴇ/ᴘᴜʀɢᴇ

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(about_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

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

:⧽ ʙʏ » {Config.OWNER_NAME}
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

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ STATS COMMAND ─═◈═────
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != Config.OWNER_ID:
            await update.message.reply_text(f"❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!\n{self.get_footer()}", parse_mode="Markdown")
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

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        await update.message.reply_text(stats_text, parse_mode="Markdown")

    # ────═◈═─ MODERATION COMMANDS ─═◈═────
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴡᴀʀɴ!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
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
{self.get_footer()}
"""
        await update.message.reply_text(warn_msg, parse_mode="Markdown")
        
        await self.log_action(chat.id, f"⚠️ **ᴡᴀʀɴ** {target.first_name} ({warn_count}/{max_warns}) ʙʏ {user.first_name} - {reason}")
        
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
{self.get_footer()}
"""
                await update.message.reply_text(mute_msg, parse_mode="Markdown")
            except:
                pass

    async def unwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴs!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
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
        
        warnings = await db.get_warnings(target.id, chat.id)
        if warnings:
            await db.clear_warnings(target.id, chat.id)
            await update.message.reply_text(f"✅ **ʀᴇᴍᴏᴠᴇᴅ ᴀʟʟ ᴡᴀʀɴs ғᴏʀ {target.first_name}!**\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"✅ **ᴜɴᴡᴀʀɴ** {target.first_name} ʙʏ {user.first_name}")
        else:
            await update.message.reply_text(f"ℹ️ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴs!\n{self.get_footer()}", parse_mode="Markdown")

    async def warns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await update.message.reply_text(f"✅ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs!\n{self.get_footer()}", parse_mode="Markdown")
            return
        
        warn_text = f"⚠️ **ᴡᴀʀɴɪɴɢs ғᴏʀ {target.first_name}:**\n\n"
        for i, warn in enumerate(warnings, 1):
            warn_text += f"└ {i}. {warn['reason']}\n"
        warn_text += self.get_footer()
        
        await update.message.reply_text(warn_text, parse_mode="Markdown")

    async def delwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        target = update.message.reply_to_message.from_user
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await context.bot.delete_message(chat.id, update.message.message_id)
        await db.add_warning(target.id, chat.id, "ᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ", user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        
        await update.message.reply_text(f"⚠️ **ᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ & ᴡᴀʀɴᴇᴅ {target.first_name}!** ({len(warnings)}/{Config.MAX_WARNINGS})\n{self.get_footer()}", parse_mode="Markdown")

    async def reset_warns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇsᴇᴛ ᴡᴀʀɴs!")
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
        await update.message.reply_text(f"✅ **ʀᴇsᴇᴛ ᴀʟʟ ᴡᴀʀɴs ғᴏʀ {target.first_name}!**\n{self.get_footer()}", parse_mode="Markdown")

    # ────═◈═─ MUTE/UNMUTE COMMANDS ─═◈═────
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴜᴛᴇ!")
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
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ᴍᴜᴛᴇ ʙᴏᴛs!")
            return
        
        duration = Config.MUTE_DURATION
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            if len(context.args) > 1 and context.args[1].isdigit():
                duration = int(context.args[1])
                reason = " ".join(context.args[2:]) if len(context.args) > 2 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
            
            await db.add_mute(target.id, chat.id, duration, reason, user.id)
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
{self.get_footer()}
"""
            await update.message.reply_text(mute_msg, parse_mode="Markdown")
            await self.log_action(chat.id, f"🔇 **ᴍᴜᴛᴇ** {target.first_name} ({duration}s) ʙʏ {user.first_name} - {reason}")
            
            asyncio.create_task(self.auto_unmute(context, chat.id, target.id, duration))
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def auto_unmute(self, context, chat_id, user_id, duration):
        await asyncio.sleep(duration)
        try:
            await db.remove_mute(user_id, chat_id)
            await context.bot.restrict_chat_member(
                chat_id,
                user_id,
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

    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇ!")
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
            await update.message.reply_text(f"🔊 **ᴜɴᴍᴜᴛᴇᴅ {target.first_name}!**\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"🔊 **ᴜɴᴍᴜᴛᴇ** {target.first_name} ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ KICK/BAN/UNBAN COMMANDS ─═◈═────
    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴋɪᴄᴋ!")
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
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"👢 **ᴋɪᴄᴋᴇᴅ {target.first_name}!**\n📝 ʀᴇᴀsᴏɴ: {reason}\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"👢 **ᴋɪᴄᴋ** {target.first_name} ʙʏ {user.first_name} - {reason}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʙᴀɴ!")
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
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ʙᴀɴ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"🚫 **ʙᴀɴɴᴇᴅ {target.first_name}!**\n📝 ʀᴇᴀsᴏɴ: {reason}\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"🚫 **ʙᴀɴ** {target.first_name} ʙʏ {user.first_name} - {reason}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴ!")
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
            await update.message.reply_text(f"✅ **ᴜɴʙᴀɴɴᴇᴅ {target.first_name}!**\n{self.get_footer()}", parse_mode="Markdown")
            await self.log_action(chat.id, f"✅ **ᴜɴʙᴀɴ** {target.first_name} ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ APPROVE/UNAPPROVE COMMANDS ─═◈═────
    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴘᴘʀᴏᴠᴇ!")
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
        
        await db.approve_user(target.id, chat.id)
        await update.message.reply_text(f"✅ **ᴀᴘᴘʀᴏᴠᴇᴅ** {target.first_name}!\n🔗 Nᴏᴡ Yᴏᴜʀ Aʀᴇ Fʀᴇᴇ.\n{self.get_footer()}", parse_mode="Markdown")
        await self.log_action(chat.id, f"✅ **ᴀᴘᴘʀᴏᴠᴇ** {target.first_name} ʙʏ {user.first_name}")

    async def unapprove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ!")
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
        
        await db.unapprove_user(target.id, chat.id)
        await update.message.reply_text(f"❌ **ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ** {target.first_name}!\n🔗 Nᴏ ᴍᴏʀᴇ ʟɪɴᴋs.\n{self.get_footer()}", parse_mode="Markdown")
        await self.log_action(chat.id, f"❌ **ᴜɴᴀᴘᴘʀᴏᴠᴇ** {target.first_name} ʙʏ {user.first_name}")

    # ────═◈═─ WELCOME/GIODBYE HANDLERS ─═◈═────
    async def welcome_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.new_chat_members:
            return
        
        chat = update.effective_chat
        settings = await db.get_settings(chat.id)
        
        if not settings.get('welcome', True):
            return
        
        for member in update.message.new_chat_members:
            if member.is_bot:
                continue
            
            await db.add_user(member.id, member.username, member.first_name)
            
            try:
                member_count = await context.bot.get_chat_member_count(chat.id)
            except:
                member_count = "?"
            
            welcome_msg = f"""
✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴘᴀʀᴛʏ!** ✨

────═◈═─ ✧◈✧ ─═◈═────
👤 **ɴᴀᴍᴇ:** {member.first_name}
📛 **ᴜsᴇʀɴᴀᴍᴇ:** @{member.username if member.username else 'N/A'}
📍 **ɢʀᴏᴜᴘ:** {chat.title}
👥 **ᴍᴇᴍʙᴇʀs:** {member_count}
────═◈═─ ✧◈✧ ─═◈═────
🌟 **ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ {Config.BOT_NAME}** 🌟
{self.get_footer()}
"""
            await context.bot.send_message(
                chat.id,
                welcome_msg,
                parse_mode="Markdown"
            )

    async def goodbye_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.left_chat_member:
            return
        
        chat = update.effective_chat
        settings = await db.get_settings(chat.id)
        
        if not settings.get('goodbye', True):
            return
        
        member = update.message.left_chat_member
        if member.is_bot:
            return
        
        goodbye_msg = f"""
💔 **ɢᴏᴏᴅʙʏᴇ!** 💔

────═◈═─ ✧◈✧ ─═◈═────
  👋 {member.first_name}     
  🚪 ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ   
  📍 {chat.title}      
✦•····················•✦

😢 ᴡᴇ ᴡɪʟʟ ᴍɪss ʏᴏᴜ!
{self.get_footer()}
"""
        await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode="Markdown"
        )

    # ────═◈═─ ANTI-SPAM/LINK/18+ HANDLERS ─═◈═────
    async def antispam_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        settings = await db.get_settings(chat.id)
        if not settings.get('antispam', True):
            return
        
        if await self.is_admin(context, chat.id, user.id):
            return
        
        if not context.user_data.get('last_message_time'):
            context.user_data['last_message_time'] = []
        
        current_time = datetime.now().timestamp()
        context.user_data['last_message_time'].append(current_time)
        
        if len(context.user_data['last_message_time']) > 10:
            context.user_data['last_message_time'] = context.user_data['last_message_time'][-10:]
        
        if len(context.user_data['last_message_time']) >= 5:
            time_diff = current_time - context.user_data['last_message_time'][-5]
            if time_diff < 5:
                await context.bot.delete_message(chat.id, update.message.message_id)
                warnings = await db.get_warnings(user.id, chat.id)
                warn_count = len(warnings)
                if warn_count < Config.MAX_WARNINGS:
                    await db.add_warning(user.id, chat.id, "sᴘᴀᴍᴍɪɴɢ", "ʙᴏᴛ")
                    await update.message.reply_text(f"⚠️ {user.first_name} ᴡᴀʀɴᴇᴅ ғᴏʀ sᴘᴀᴍ! ({warn_count+1}/{Config.MAX_WARNINGS})")

    async def antilink_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        settings = await db.get_settings(chat.id)
        if not settings.get('antilink', False):
            return
        
        if await self.is_admin(context, chat.id, user.id):
            return
        
        is_approved = await db.is_approved(user.id, chat.id)
        if is_approved:
            return
        
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        if url_pattern.search(update.message.text):
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(
                f"🔗 **ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ!**\n\n{user.first_name}, ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ᴛᴏ sᴇɴᴅ ʟɪɴᴋs.\nᴄᴏɴᴛᴀᴄᴛ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴀᴘᴘʀᴏᴠᴀʟ.",
                parse_mode="Markdown"
            )

    async def anti18_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        settings = await db.get_settings(chat.id)
        if not settings.get('anti18', True):
            return
        
        if await self.is_admin(context, chat.id, user.id):
            return
        
        adult_keywords = ['porn', 'xxx', 'sex', 'nude', 'nsfw', '18+', 'adult']
        if any(keyword in update.message.text.lower() for keyword in adult_keywords):
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(
                f"🔞 **18+ ᴄᴏɴᴛᴇɴᴛ ᴅᴇᴛᴇᴄᴛᴇᴅ!**\n\n{user.first_name}, ᴛʜɪs ᴛʏᴘᴇ ᴏғ ᴄᴏɴᴛᴇɴᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ.",
                parse_mode="Markdown"
            )

    # ────═◈═─ CALLBACK HANDLER ─═◈═────
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
        
        if data == "main_menu":
            keyboard = [
                [InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")],
                [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
                [InlineKeyboardButton("👥 sᴛᴀғғ", callback_data="staff")]
            ]
            if is_premium:
                keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
            
            try:
                await query.edit_message_text(
                    f"🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif data == "staff":
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(
                    f"👥 ᴜsᴇ /staff ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"👥 ᴜsᴇ /staff ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif data == "about":
            text = f"""
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
╰┈➤ ᴀɴᴛɪ-18+
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ
╰┈➤ ᴘɪɴ/ᴜɴᴘɪɴ
╰┈➤ ᴅᴇʟᴇᴛᴇ/ᴘᴜʀɢᴇ

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "help":
            text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

**👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /warn @user - ᴡᴀʀɴ ᴜsᴇʀ
╰┈➤ /unwarn @user - ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴ
╰┈➤ /warns @user - ᴄʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /delwarn - ᴅᴇʟᴇᴛᴇ & ᴡᴀʀɴ
╰┈➤ /resetwarns @user - ʀᴇsᴇᴛ ᴡᴀʀɴs
╰┈➤ /mute @user - ᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /unmute @user - ᴜɴᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /kick @user - ᴋɪᴄᴋ ᴜsᴇʀ
╰┈➤ /ban @user - ʙᴀɴ ᴜsᴇʀ
╰┈➤ /unban @user - ᴜɴʙᴀɴ ᴜsᴇʀ
╰┈➤ /pin - ᴘɪɴ ᴍᴇssᴀɢᴇ
╰┈➤ /unpin - ᴜɴᴘɪɴ
╰┈➤ /del - ᴅᴇʟᴇᴛᴇ
╰┈➤ /logdel - ᴅᴇʟᴇᴛᴇ & ʟᴏɢ
╰┈➤ /purge - ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs
╰┈➤ /reload - ʀᴇғʀᴇsʜ ᴀᴅᴍɪɴs
╰┈➤ /settings - ᴍᴀɴᴀɢᴇ sᴇᴛᴛɪɴɢs
╰┈➤ /setrules - sᴇᴛ ʀᴜʟᴇs
╰┈➤ /rules - ᴠɪᴇᴡ ʀᴜʟᴇs
╰┈➤ /approve @user - ᴀᴘᴘʀᴏᴠᴇ ᴜsᴇʀ
╰┈➤ /unapprove @user - ʀᴇᴠᴏᴋᴇ ᴀᴘᴘʀᴏᴠᴀʟ

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ
╰┈➤ /ping - ᴄʜᴇᴄᴋ ʙᴏᴛ
╰┈➤ /staff - ᴠɪᴇᴡ sᴛᴀғғ
╰┈➤ /info @user - ᴜsᴇʀ ɪɴғᴏ
╰┈➤ /infopvt @user - ᴜsᴇʀ ɪɴғᴏ ᴘʀɪᴠᴀᴛᴇ
╰┈➤ /me - ʏᴏᴜʀ ɪɴғᴏ
╰┈➤ /geturl - ɢᴇᴛ ᴍᴇssᴀɢᴇ ʟɪɴᴋ
╰┈➤ /pinned - ᴠɪᴇᴡ ᴘɪɴɴᴇᴅ

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "stats":
            if user_id != Config.OWNER_ID:
                try:
                    await query.edit_message_text(f"❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!\n{self.get_footer()}", parse_mode="Markdown")
                except:
                    await query.message.reply_text(f"❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!\n{self.get_footer()}", parse_mode="Markdown")
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

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 ᴀɴᴛɪ-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(
                    f"⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
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

:⧽ ʙʏ » {Config.OWNER_NAME}
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

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            try:
                await query.edit_message_text(f"✅ **{setting.upper()}** {'ᴇɴᴀʙʟᴇᴅ' if not current else 'ᴅɪsᴀʙʟᴇᴅ'}!\n{self.get_footer()}", parse_mode="Markdown")
            except:
                await query.message.reply_text(f"✅ **{setting.upper()}** {'ᴇɴᴀʙʟᴇᴅ' if not current else 'ᴅɪsᴀʙʟᴇᴅ'}!\n{self.get_footer()}", parse_mode="Markdown")
            
            await asyncio.sleep(1)
            
            keyboard = [
                [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 ᴀɴᴛɪ-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(
                    f"⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif data in ["set_welcome", "set_goodbye", "set_antispam", "set_antilink", "set_anti18"]:
            setting_map = {
                "set_welcome": "welcome",
                "set_goodbye": "goodbye",
                "set_antispam": "antispam",
                "set_antilink": "antilink",
                "set_anti18": "anti18"
            }
            setting = setting_map.get(data, "welcome")
            settings = await db.get_settings(update.effective_chat.id)
            current = settings.get(setting, True)
            keyboard = [
                [InlineKeyboardButton(f"{'✅' if current else '❌'} ᴛᴏɢɢʟᴇ", callback_data=f"toggle_{setting}")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings")]
            ]
            display_name = data.replace("set_", "").upper()
            try:
                await query.edit_message_text(
                    f"{display_name}\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n{self.get_footer()}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"{display_name}\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n{self.get_footer()}",
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
                    f"❌ **ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ!**\n"
                    f"ᴇʀʀᴏʀ: `{str(context.error)[:100]}`\n{self.get_footer()}",
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
