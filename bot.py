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
import psutil
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
from handles import Handlers
from keyboards import Keyboards

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()
handlers = Handlers()

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
        self.start_time = datetime.now()
        premium_print(f"ʙᴏᴛ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ: {Config.BOT_NAME}", "🚀")
        premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
        premium_print(f"ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs: ʟᴏᴀᴅᴇᴅ", "💎")

    def get_owner_credit(self):
        return f"\n\n<b>👑 Cʀᴇᴀᴛᴇᴅ ʙʏ: {Config.OWNER_NAME}</b>"

    # ────═◈═─ CALLBACK HANDLER ─═◈═────
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
        
        if data == "main_menu":
            user = update.effective_user
            main_text = f"""
╔═══════════════════════════════════╗
║  ⚡ <b>PIKACHU PROTECTION BOT</b> ⚡
╚═══════════════════════════════════╝

✨ <b>Hᴇʟʟᴏ {user.first_name}!</b> ✨

I ᴀᴍ ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ!

<b>🔰 Pᴏᴡᴇʀғᴜʟ Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ 🛡️ Aɴᴛɪ-Sᴘᴀᴍ & Lɪɴᴋ Sʜɪᴇʟᴅ
╰┈➤ ⚠️ Wᴀʀɴ/Mᴜᴛᴇ/Bᴀɴ/Kɪᴄᴋ
╰┈➤ 📌 Pɪɴ/Uɴᴘɪɴ/Dᴇʟᴇᴛᴇ/Pᴜʀɢᴇ
╰┈➤ 👋 Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ
╰┈➤ 👥 Aᴅᴠᴀɴᴄᴇᴅ Rᴏʟᴇs Sʏsᴛᴇᴍ
╰┈➤ 🔄 SG (Uꜱᴇʀ Hɪsᴛᴏʀʏ)
╰┈➤ 📜 Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ
╰┈➤ 💬 Sᴍᴀʀᴛ Cʜᴀᴛ

💎 <b>Pʀᴇᴍɪᴜᴍ Sᴛᴀᴛᴜs:</b> {'✅ Aᴄᴛɪᴠᴇ' if is_premium else '❌ Iɴᴀᴄᴛɪᴠᴇ'}

📌 <b>Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!</b>
{self.get_owner_credit()}
"""
            keyboard = Keyboards.main_menu(is_premium)
            try:
                await query.edit_message_text(
                    main_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except:
                await query.message.reply_text(
                    main_text,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            return

        elif data == "stats":
            if user_id != Config.OWNER_ID:
                try:
                    await query.edit_message_text("❌ Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!", parse_mode="HTML")
                except:
                    await query.message.reply_text("❌ Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!", parse_mode="HTML")
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
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        elif data == "settings":
            keyboard = Keyboards.settings_menu()
            try:
                await query.edit_message_text(
                    f"⚙️ <b>Sᴇᴛᴛɪɴɢs Mᴇɴᴜ</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except:
                await query.message.reply_text(
                    f"⚙️ <b>Sᴇᴛᴛɪɴɢs Mᴇɴᴜ</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            return

        elif data == "help":
            help_text = f"""
📖 <b>POWERFUL COMMANDS LIST</b> 📖

<b>👑 Fᴏᴜɴᴅᴇʀ & Cᴏ-Fᴏᴜɴᴅᴇʀ:</b>
/cofounder, /uncofounder
/mod, /unmod
/muter, /unmuter
/cleaner, /uncleaner
/helper, /unhelper
/free, /unfree

<b>👮 Aᴅᴍɪɴ & Mᴏᴅᴇʀᴀᴛᴏʀ:</b>
/reload, /settings
/ban, /unban, /kick
/mute, /unmute
/warn, /unwarn, /warns

<b>📌 Pɪɴ Mᴇssᴀɢᴇs:</b>
/pin, /unpin, /pinned

<b>🗑️ Dᴇʟᴇᴛᴇ:</b>
/del, /logdel, /purge

<b>📊 Gᴇɴᴇʀᴀʟ:</b>
/start, /help, /about
/ping, /staff
/info, /infopvt, /me
/geturl, /sg, /history
/chat, /filter, /filters

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

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
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        elif data == "staff":
            try:
                await query.edit_message_text("👥 Uꜱᴇ /sᴛᴀғғ ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ!", parse_mode="HTML")
            except:
                await query.message.reply_text("👥 Uꜱᴇ /sᴛᴀғғ ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ!", parse_mode="HTML")
            return

        elif data == "sg":
            text = f"""
🔄 <b>SG - Uꜱᴇʀ Hɪsᴛᴏʀʏ</b>

Uꜱᴇ /sg @ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ
Tᴏ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴄᴏᴍᴘʟᴇᴛᴇ ʜɪsᴛᴏʀʏ!{self.get_owner_credit()}
"""
            try:
                await query.edit_message_text(text, parse_mode="HTML")
            except:
                await query.message.reply_text(text, parse_mode="HTML")
            return

        elif data == "history":
            text = f"""
📜 <b>Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ</b>

Uꜱᴇ /history @ᴜsᴇʀɴᴀᴍᴇ
Tᴏ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴄᴏᴍᴘʟᴇᴛᴇ ᴄʜᴀɴɢᴇ ʜɪsᴛᴏʀʏ!{self.get_owner_credit()}
"""
            try:
                await query.edit_message_text(text, parse_mode="HTML")
            except:
                await query.message.reply_text(text, parse_mode="HTML")
            return

        elif data == "chat":
            text = f"""
💬 <b>Cʜᴀᴛ ᴡɪᴛʜ ᴍᴇ!</b>

Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴀɴᴅ I'ʟʟ ʀᴇsᴘᴏɴᴅ!{self.get_owner_credit()}
"""
            try:
                await query.edit_message_text(text, parse_mode="HTML")
            except:
                await query.message.reply_text(text, parse_mode="HTML")
            return

        elif data == "roles":
            keyboard = Keyboards.role_keyboard()
            try:
                await query.edit_message_text(
                    f"👑 <b>Uꜱᴇʀ Rᴏʟᴇs</b>\n\nSᴇʟᴇᴄᴛ ᴀ ʀᴏʟᴇ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ:{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            except:
                await query.message.reply_text(
                    f"👑 <b>Uꜱᴇʀ Rᴏʟᴇs</b>\n\nSᴇʟᴇᴄᴛ ᴀ ʀᴏʟᴇ ᴛᴏ ʟᴇᴀʀɴ ᴍᴏʀᴇ:{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
            return

        elif data.startswith("role_"):
            role_name = data.replace("role_", "").upper()
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
            desc = descriptions.get(role_name, "")
            text = f"""
👑 <b>{role_name} Rᴏʟᴇ</b>

Tᴏ ᴀᴅᴅ ᴛʜɪs ʀᴏʟᴇ: /{role_name.lower()} @ᴜsᴇʀ
Tᴏ ʀᴇᴍᴏᴠᴇ ᴛʜɪs ʀᴏʟᴇ: /un{role_name.lower()} @ᴜsᴇʀ

<b>Dᴇsᴄʀɪᴘᴛɪᴏɴ:</b>
{desc}{self.get_owner_credit()}
"""
            try:
                await query.edit_message_text(text, parse_mode="HTML")
            except:
                await query.message.reply_text(text, parse_mode="HTML")
            return

        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            text = f"✅ <b>{setting.upper()}</b> {'Enabled' if not current else 'Disabled'}!{self.get_owner_credit()}"
            try:
                await query.edit_message_text(text, parse_mode="HTML")
            except:
                await query.message.reply_text(text, parse_mode="HTML")
            return

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

<b>Pʀɪᴄᴇ:</b> $5/ᴍᴏɴᴛʜ

Cᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ Tᴏ Bᴜʏ:
📞 {Config.OWNER_USERNAME}

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

    # ────═◈═─ RUN BOT ─═◈═────
    def run(self):
        try:
            # Build application with updater
            self.app = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Command handlers - Using handlers from handles.py
            self.app.add_handler(CommandHandler("start", handlers.start))
            self.app.add_handler(CommandHandler("help", handlers.help_command))
            self.app.add_handler(CommandHandler("warn", handlers.warn_command))
            self.app.add_handler(CommandHandler("warns", handlers.warns_command))
            self.app.add_handler(CommandHandler("resetwarns", handlers.resetwarns_command))
            self.app.add_handler(CommandHandler("mute", handlers.mute_command))
            self.app.add_handler(CommandHandler("unmute", handlers.unmute_command))
            self.app.add_handler(CommandHandler("kick", handlers.kick_command))
            self.app.add_handler(CommandHandler("ban", handlers.ban_command))
            self.app.add_handler(CommandHandler("unban", handlers.unban_command))
            
            # Callback handler
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            
            # Message handlers
            self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handlers.welcome_handler))
            self.app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handlers.goodbye_handler))
            
            # Error handler
            self.app.add_error_handler(self.error_handler)
            
            premium_print(f"ʙᴏᴛ {Config.BOT_NAME} ɪs ɴᴏᴡ ʀᴜɴɴɪɴɢ!", "⚡")
            premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
            
            self.app.run_polling()
        except Exception as e:
            premium_print(f"ᴇʀʀᴏʀ: {str(e)}", "❌")
            sys.exit(1)

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

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        premium_print("ʙᴏᴛ ᴛᴏᴋᴇɴ ɴᴏᴛ ғᴏᴜɴᴅ!", "❌")
        sys.exit(1)
    
    bot = PikachuProtectionBot()
    bot.run()
