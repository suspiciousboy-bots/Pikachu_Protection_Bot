#!/usr/bin/env python3
"""
⚡ PIKACHU X PROTECTION BOT - ULTIMATE GROUP MANAGEMENT ⚡
"""

import os
import sys
import asyncio
import logging
import threading
import io
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
    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

threading.Thread(target=run_web, daemon=True).start()
print("🌐 Web server started")
# ──────────────────────────────────────────────────

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import Config
from database import Database
from keyboards import Keyboards

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

# Welcome Image URL
WELCOME_IMAGE = "https://i.ibb.co/7NT4SDXy/file-124.jpg"

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

    # ────═◈═─ HELPER: GET TARGET USER ─═◈═────
    async def _get_target_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get target user from reply or username or ID"""
        target = None
        
        # Check if reply to a message
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
            return target
        
        # Check if username or ID provided
        if context.args:
            username = context.args[0].strip()
            
            # Remove @ if present
            if username.startswith('@'):
                username = username[1:]
            
            # Try to get user by username
            try:
                # Try with @ symbol first
                try:
                    target = await context.bot.get_chat(f"@{username}")
                    if target:
                        return target
                except:
                    pass
                
                # Try without @ symbol
                try:
                    target = await context.bot.get_chat(username)
                    if target:
                        return target
                except:
                    pass
                
                # Try as user ID
                try:
                    user_id = int(username)
                    target = await context.bot.get_chat(user_id)
                    if target:
                        return target
                except:
                    pass
                    
            except Exception as e:
                logger.error(f"Error getting user: {e}")
                pass
        
        return None

    # ────═◈═─ LOCK TYPES ─═◈═────
    LOCK_TYPES = {
        'all': '🔒 All messages',
        'album': '🖼️ Album',
        'anonchannel': '📢 Anonymous Channel',
        'audio': '🎵 Audio',
        'bot': '🤖 Bot commands',
        'botlink': '🔗 Bot links',
        'button': '🔘 Buttons',
        'cashtag': '💰 Cashtags',
        'checklist': '✅ Checklist',
        'cjk': '🈴 CJK characters',
        'command': '📝 Commands',
        'comment': '💬 Comments',
        'contact': '📇 Contacts',
        'cyrillic': '🅰️ Cyrillic',
        'document': '📄 Documents',
        'email': '📧 Emails',
        'emoji': '😊 Emojis',
        'emojicustom': '🎨 Custom emojis',
        'emojigame': '🎮 Emoji games',
        'emojionly': '😃 Emoji only',
        'externalreply': '↩️ External replies',
        'forward': '↗️ Forwards',
        'forwardbot': '🤖 Bot forwards',
        'forwardchannel': '📢 Channel forwards',
        'forwardstory': '📖 Story forwards',
        'forwarduser': '👤 User forwards',
        'game': '🎮 Games',
        'gif': '🎞️ GIFs',
        'guestbot': '👻 Guest bots',
        'inline': '🔗 Inline',
        'invitelink': '🔗 Invite links',
        'location': '📍 Location',
        'outsidereaction': '👀 Outside reactions',
        'phone': '📞 Phone numbers',
        'photo': '📸 Photos',
        'poll': '📊 Polls',
        'reaction': '😊 Reactions',
        'rtl': '↔️ RTL text',
        'spoiler': '🔵 Spoilers',
        'sticker': '🎨 Stickers',
        'stickermanimated': '🎭 Animated stickers',
        'stickerpremium': '💎 Premium stickers',
        'text': '📝 Text messages',
        'videonote': '🎥 Video notes',
        'voice': '🎤 Voice messages',
        'zalgo': '🔥 Zalgo text'
    }

    # ────═◈═─ LOCK/UNLOCK COMMANDS ─═◈═────

    async def locktypes_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all available lock types in a beautiful format"""
        text = """
╔═══════════════════════════════════════════════════════════╗
║              📋 Aᴠᴀɪʟᴀʙʟᴇ Lᴏᴄᴋ Tʏᴘᴇs                  ║
╚═══════════════════════════════════════════════════════════╝

"""
        # Group lock types into columns
        items = list(self.LOCK_TYPES.items())
        for i in range(0, len(items), 3):
            row = items[i:i+3]
            line = ""
            for key, name in row:
                line += f"  {name:<18}"
            text += line + "\n"
            line2 = ""
            for key, name in row:
                line2 += f"  <code>/{key}</code>{' ' * (18 - len(key) - 6)}"
            text += line2 + "\n\n"

        text += """
═══════════════════════════════════════════════════════════

<b>📌 Usᴀɢᴇ:</b>
/lock (type)     - Lᴏᴄᴋ ᴀ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ
/unlock (type)   - Uɴʟᴏᴄᴋ ᴀ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ

<b>🔹 Example:</b>
/lock text       - Lᴏᴄᴋ ᴛᴇxᴛ ᴍᴇssᴀɢᴇs
/unlock text     - Uɴʟᴏᴄᴋ ᴛᴇxᴛ ᴍᴇssᴀɢᴇs

:⧽ ʙʏ: {Config.OWNER_NAME}
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async def lock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lock a specific message type in the group"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
        
        # Check admin permission
        user = update.effective_user
        chat = update.effective_chat
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                return await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʟᴏᴄᴋ ᴄʜᴀᴛ!")
        except:
            return await update.message.reply_text("❌ Eʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ᴘᴇʀᴍɪssɪᴏɴs!")
        
        if not context.args:
            return await update.message.reply_text("⚠️ Usᴀɢᴇ: /lock (type)\n\nTʏᴘᴇs: /locktypes")
        
        lock_type = context.args[0].lower()
        if lock_type not in self.LOCK_TYPES:
            return await update.message.reply_text(f"❌ Uɴᴋɴᴏᴡɴ ʟᴏᴄᴋ ᴛʏᴘᴇ: <code>{lock_type}</code>\n\nCʜᴇᴄᴋ /locktypes ғᴏʀ ᴀʟʟ ᴛʏᴘᴇs!", parse_mode=ParseMode.HTML)
        
        # Save lock setting in database
        settings = await db.get_settings(chat.id)
        locks = settings.get('locks', {})
        locks[lock_type] = True
        await db.update_settings(chat.id, 'locks', locks)
        
        # Apply lock using Telegram's restrict permissions
        if lock_type == 'all':
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False
            )
            await context.bot.set_chat_permissions(chat.id, permissions)
        elif lock_type == 'text':
            permissions = ChatPermissions(
                can_send_messages=False,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await context.bot.set_chat_permissions(chat.id, permissions)
        elif lock_type in ['audio', 'document', 'photo', 'video', 'videonote', 'voice']:
            # For specific media types, we need to handle individually
            pass
        
        await update.message.reply_text(f"✅ <b>Lᴏᴄᴋᴇᴅ</b> <code>{lock_type}</code> - {self.LOCK_TYPES.get(lock_type, lock_type)}!", parse_mode=ParseMode.HTML)

    async def unlock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unlock a specific message type in the group"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
        
        # Check admin permission
        user = update.effective_user
        chat = update.effective_chat
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                return await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʟᴏᴄᴋ ᴄʜᴀᴛ!")
        except:
            return await update.message.reply_text("❌ Eʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ᴘᴇʀᴍɪssɪᴏɴs!")
        
        if not context.args:
            return await update.message.reply_text("⚠️ Usᴀɢᴇ: /unlock (type)\n\nTʏᴘᴇs: /locktypes")
        
        lock_type = context.args[0].lower()
        if lock_type not in self.LOCK_TYPES:
            return await update.message.reply_text(f"❌ Uɴᴋɴᴏᴡɴ ʟᴏᴄᴋ ᴛʏᴘᴇ: <code>{lock_type}</code>\n\nCʜᴇᴄᴋ /locktypes ғᴏʀ ᴀʟʟ ᴛʏᴘᴇs!", parse_mode=ParseMode.HTML)
        
        # Remove lock setting from database
        settings = await db.get_settings(chat.id)
        locks = settings.get('locks', {})
        locks[lock_type] = False
        await db.update_settings(chat.id, 'locks', locks)
        
        # Unlock - restore all permissions
        if lock_type == 'all':
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await context.bot.set_chat_permissions(chat.id, permissions)
        else:
            # Unlock specific type - restore all permissions
            permissions = ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            await context.bot.set_chat_permissions(chat.id, permissions)
        
        await update.message.reply_text(f"✅ <b>Uɴʟᴏᴄᴋᴇᴅ</b> <code>{lock_type}</code> - {self.LOCK_TYPES.get(lock_type, lock_type)}!", parse_mode=ParseMode.HTML)

    # ────═◈═─ GENERAL COMMANDS ─═◈═────
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        is_premium = await db.is_premium(user.id)
        await db.add_user(user.id, user.username, user.first_name)
        
        text = f"""
✨ <b>Wᴇʟᴄᴏᴍᴇ ᴛᴏ {Config.BOT_NAME}</b> ✨

────═◈═─ ✧◈✧ ─═◈═────
🤖 <b>Bᴏᴛ:</b> {Config.BOT_NAME}  
👤 <b>Uꜱᴇʀ:</b> {user.first_name} 
💎 <b>Pʀᴇᴍɪᴜᴍ:</b> { '✅ Aᴄᴛɪᴠᴇ' if is_premium else '❌ Iɴᴀᴄᴛɪᴠᴇ' } 
✦•····················•✦

🌟 <b>Fᴇᴀᴛᴜʀᴇs:</b>  
╰┈➤ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ  
╰┈➤ Aɴᴛɪ-Sᴘᴀᴍ  
╰┈➤ Aɴᴛɪ-Lɪɴᴋ  
╰┈➤ Wᴀʀɴ/Mᴜᴛᴇ/Bᴀɴ/Kɪᴄᴋ  
╰┈➤ Lᴏᴄᴋ/Uɴʟᴏᴄᴋ Cʜᴀᴛ  
╰┈➤ Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs  

👑 <b>Oᴡɴᴇʀ:</b> {Config.OWNER_NAME}
📢 <b>Usᴇ /help ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs</b>
"""
        keyboard = Keyboards.main_menu(is_premium)
        await update.message.reply_photo(photo=WELCOME_IMAGE, caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = f"""
📖 <b>Cᴏᴍᴍᴀɴᴅ Lɪsᴛ</b> 📖

<b>🔒 Lᴏᴄᴋ Cᴏᴍᴍᴀɴᴅs:</b>
/lock (type) - Lᴏᴄᴋ ᴀ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ
/unlock (type) - Uɴʟᴏᴄᴋ ᴀ ᴍᴇssᴀɢᴇ ᴛʏᴘᴇ
/locktypes - Sʜᴏᴡ ᴀʟʟ ʟᴏᴄᴋ ᴛʏᴘᴇs

<b>👑 Aᴅᴍɪɴ:</b> /warn, /unwarn, /warns, /delwarn, /resetwarns
/mute, /unmute, /kick, /ban, /unban, /approve, /unapprove
/settings, /reload

<b>📌 Pɪɴ:</b> /pin, /unpin, /pinned, /editpin, /delpin
<b>🗑️ Dᴇʟᴇᴛᴇ:</b> /del, /logdel, /purge

<b>👑 Rᴏʟᴇs:</b> /cofounder, /uncofounder, /mod, /unmod
/muter, /unmuter, /cleaner, /uncleaner, /helper, /unhelper
/free, /unfree

<b>📊 Gᴇɴᴇʀᴀʟ:</b> /start, /help, /about, /ping, /staff
/info, /infopvt, /me, /geturl, /sg, /history, /chat
/roles, /premium, /enablewelcome, /disablewelcome

<b>🔰 Fɪʟᴛᴇʀ:</b> /filter, /stopfilter, /filters

🔥 Pᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = f"""
⚡ <b>Aʙᴏᴜᴛ {Config.BOT_NAME}</b> ⚡
🤖 <b>Nᴀᴍᴇ:</b> {Config.BOT_NAME}  
👑 <b>Oᴡɴᴇʀ:</b> {Config.OWNER_NAME} 
📞 <b>Cᴏɴᴛᴀᴄᴛ:</b> {Config.OWNER_USERNAME} 
📢 <b>Vᴇʀsɪᴏɴ:</b> 3.0.0
🔰 <b>Sᴛᴀᴛᴜs:</b> Aᴄᴛɪᴠᴇ
👑 <b>Bʏ:</b> {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        start = datetime.now()
        msg = await update.message.reply_text("🏓 Pɪɴɢɪɴɢ...")
        end = datetime.now()
        latency = (end - start).microseconds / 1000
        
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            ram_used = ram.used / (1024 ** 3)
            ram_total = ram.total / (1024 ** 3)
        except:
            cpu = "N/A"
            ram_used = "N/A"
            ram_total = "N/A"
        
        text = f"""
⚡️ <b>{Config.BOT_NAME}</b>
🏓 ᴘɪɴɢ: <code>{latency:.3f}ᴍs</code>
:⧽ ᴄᴩᴜ: <code>{cpu}%</code>
:⧽ ʀᴀᴍ: <code>{ram_used:.2f}GB / {ram_total:.2f}GB</code>
:⧽ ʙʏ: {Config.OWNER_NAME}
"""
        await msg.edit_text(text, parse_mode=ParseMode.HTML)

    async def staff_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
        
        chat = update.effective_chat
        admins = await context.bot.get_chat_administrators(chat.id)
        owner = None
        admin_list = []
        for admin in admins:
            if admin.status == 'creator':
                owner = admin.user
            else:
                admin_list.append(admin.user)
        
        text = f"👥 <b>Sᴛᴀғғ Lɪsᴛ</b>\n\n👑 <b>Oᴡɴᴇʀ:</b> {owner.first_name}\n\n👔 <b>Aᴅᴍɪɴs: ({len(admin_list)})</b>\n"
        for admin in admin_list:
            text += f"╰┈➤ {admin.first_name}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = await self._get_target_user(update, context)
        if not target:
            target = update.effective_user
        
        stats = await db.get_user_stats(target.id)
        text = f"""
📋 <b>Uꜱᴇʀ Iɴғᴏ</b>
👤 <b>Nᴀᴍᴇ:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
⚠️ <b>Wᴀʀɴs:</b> {stats.get('warns', 0)}
:⧽ ʙʏ: {Config.OWNER_NAME}
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async def infopvt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = await self._get_target_user(update, context)
        if not target:
            target = update.effective_user
        
        stats = await db.get_user_stats(target.id)
        text = f"""
📋 <b>Uꜱᴇʀ Iɴғᴏ</b>
👤 <b>Nᴀᴍᴇ:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
⚠️ <b>Wᴀʀɴs:</b> {stats.get('warns', 0)}
"""
        await context.bot.send_message(update.effective_user.id, text, parse_mode=ParseMode.HTML)
        await update.message.reply_text("✅ Iɴғᴏ sᴇɴᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ!")

    async def me_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        stats = await db.get_user_stats(user.id)
        text = f"""
📋 <b>Yᴏᴜʀ Iɴғᴏ</b>
👤 <b>Nᴀᴍᴇ:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
⚠️ <b>Wᴀʀɴs:</b> {stats.get('warns', 0)}
:⧽ ʙʏ: {Config.OWNER_NAME}
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async def geturl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
        chat = update.effective_chat
        msg = update.message.reply_to_message
        link = f"https://t.me/{chat.username}/{msg.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{msg.message_id}"
        await update.message.reply_text(f"🔗 <b>Lɪɴᴋ:</b>\n{link}", parse_mode=ParseMode.HTML)

    async def sg_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ!\n\nUsᴀɢᴇ:\n/sg @username\n/sg (user_id)\n/sg (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        
        history = await db.get_user_history(target.id)
        if not history:
            return await update.message.reply_text(f"📋 Nᴏ ʜɪsᴛᴏʀʏ ғᴏʀ {target.first_name}!")
        
        text = f"🔄 <b>Hɪsᴛᴏʀʏ - {target.first_name}</b>\n\n"
        for i, entry in enumerate(history[:5], 1):
            text += f"└ {i}. {entry.get('first_name', 'N/A')} (@{entry.get('username', 'N/A')})\n"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ!\n\nUsᴀɢᴇ:\n/history @username\n/history (user_id)\n/history (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        
        history = await db.get_user_history(target.id)
        if not history:
            return await update.message.reply_text(f"📋 Nᴏ ʜɪsᴛᴏʀʏ ғᴏʀ {target.first_name}!")
        
        content = f"USER HISTORY - {target.first_name}\n\n"
        for entry in history:
            content += f"Name: {entry.get('first_name', 'N/A')} | @{entry.get('username', 'N/A')}\n"
        
        file = io.BytesIO(content.encode('utf-8'))
        file.name = f"history_{target.id}.txt"
        await context.bot.send_document(chat_id=update.effective_chat.id, document=file)

    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"💬 <b>Cʜᴀᴛ ᴡɪᴛʜ Mᴇ!</b>\n\nSᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ!\n:⧽ ʙʏ: {Config.OWNER_NAME}", parse_mode=ParseMode.HTML)

    async def roles_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = f"""
👑 <b>Uꜱᴇʀ Rᴏʟᴇs</b>
<b>Fᴏᴜɴᴅᴇʀ:</b> Aʟʟ ᴘᴏᴡᴇʀs
<b>Cᴏ-Fᴏᴜɴᴅᴇʀ:</b> Mᴀɴᴀɢᴇs sᴛᴀғғ
<b>Aᴅᴍɪɴ:</b> Gʀᴏᴜᴘ ᴀᴅᴍɪɴ
<b>Mᴏᴅ:</b> Mᴏᴅᴇʀᴀᴛᴇs ᴜsᴇʀs
<b>Mᴜᴛᴇʀ:</b> Cᴀɴ ᴍᴜᴛᴇ
<b>Cʟᴇᴀɴᴇʀ:</b> Cᴀɴ ᴅᴇʟᴇᴛᴇ
<b>Hᴇʟᴘᴇʀ:</b> Sᴛᴀғғ ʟɪsᴛ
<b>Fʀᴇᴇ:</b> Iɢɴᴏʀᴇᴅ ʙʏ ᴀᴜᴛᴏ-ᴘᴜɴɪsʜᴍᴇɴᴛ
:⧽ ʙʏ: {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        is_premium = await db.is_premium(user.id)
        
        if is_premium:
            text = f"💎 <b>Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴇ!</b>\n✅ Yᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!"
        else:
            text = f"💎 <b>Pʀᴇᴍɪᴜᴍ Pʟᴀɴ</b>\n💰 $5/ᴍᴏɴᴛʜ\n📞 {Config.OWNER_USERNAME}"
        
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ WELCOME SETTINGS ─═◈═────

    async def enable_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        await db.update_settings(update.effective_chat.id, "welcome", True)
        await update.message.reply_text("✅ <b>Wᴇʟᴄᴏᴍᴇ ᴇɴᴀʙʟᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    async def disable_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        await db.update_settings(update.effective_chat.id, "welcome", False)
        await update.message.reply_text("❌ <b>Wᴇʟᴄᴏᴍᴇ ᴅɪsᴀʙʟᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    # ────═◈═─ WELCOME HANDLER ─═◈═────

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
            stats = await db.get_user_stats(member.id)
            
            text = f"""
🎉 <b>Wᴇʟᴄᴏᴍᴇ!</b> 🎉
👤 <b>Nᴀᴍᴇ:</b> {member.first_name}
🆔 <b>ID:</b> <code>{member.id}</code>
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
:⧽ ʙʏ: {Config.OWNER_NAME}
"""
            await context.bot.send_photo(chat_id=chat.id, photo=WELCOME_IMAGE, caption=text, parse_mode=ParseMode.HTML)

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
        await context.bot.send_message(chat.id, f"💔 <b>Gᴏᴏᴅʙʏᴇ!</b>\n<b>Uꜱᴇʀ:</b> {member.first_name}", parse_mode=ParseMode.HTML)

    # ────═◈═─ SETTINGS ─═◈═────

    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        keyboard = Keyboards.settings_menu()
        await update.message.reply_text("⚙️ <b>Sᴇᴛᴛɪɴɢs</b>", parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        admins = await context.bot.get_chat_administrators(update.effective_chat.id)
        admin_ids = [admin.user.id for admin in admins]
        await db.update_settings(update.effective_chat.id, "admins", admin_ids)
        await update.message.reply_text("✅ <b>Aᴅᴍɪɴs ʀᴇʟᴏᴀᴅᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    # ────═◈═─ MODERATION COMMANDS ─═◈═────

    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                return await update.message.reply_text("❌ Aᴅᴍɪɴ ᴏɴʟʏ!")
        except:
            return
        
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/warn @username\n/warn (user_id)\n/warn (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        
        if target.is_bot:
            return await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴡᴀʀɴ ʙᴏᴛ!")
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ"
        await db.add_warning(target.id, chat.id, reason, user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        settings = await db.get_settings(chat.id)
        max_warns = settings.get('warn_limit', 3)
        
        await update.message.reply_text(f"⚠️ <b>Wᴀʀɴɪɴɢ!</b>\n<b>Uꜱᴇʀ:</b> {target.first_name}\n<b>Wᴀʀɴ:</b> {len(warnings)}/{max_warns}\n<b>Rᴇᴀsᴏɴ:</b> {reason}", parse_mode=ParseMode.HTML)

    async def unwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/unwarn @username\n/unwarn (user_id)\n/unwarn (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        await db.clear_warnings(target.id, update.effective_chat.id)
        await update.message.reply_text(f"✅ <b>Wᴀʀɴs ʀᴇᴍᴏᴠᴇᴅ ғᴏʀ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def warns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            target = update.effective_user
        
        warnings = await db.get_warnings(target.id, update.effective_chat.id)
        if not warnings:
            return await update.message.reply_text(f"✅ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴs!")
        text = f"⚠️ <b>Wᴀʀɴs ғᴏʀ {target.first_name}:</b>\n"
        for i, w in enumerate(warnings, 1):
            text += f"└ {i}. {w['reason']}\n"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async def delwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
        target = update.message.reply_to_message.from_user
        try:
            await context.bot.delete_message(update.effective_chat.id, update.message.reply_to_message.message_id)
        except:
            pass
        await db.add_warning(target.id, update.effective_chat.id, "Dᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ", update.effective_user.id)
        await update.message.reply_text(f"⚠️ <b>Dᴇʟᴇᴛᴇᴅ & ᴡᴀʀɴᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def resetwarns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/resetwarns @username\n/resetwarns (user_id)\n/resetwarns (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        await db.clear_warnings(target.id, update.effective_chat.id)
        await update.message.reply_text(f"✅ <b>Wᴀʀɴs ʀᴇsᴇᴛ ғᴏʀ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                return await update.message.reply_text("❌ Aᴅᴍɪɴ ᴏɴʟʏ!")
        except:
            return
        
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/mute @username\n/mute (user_id)\n/mute (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        
        if target.is_bot:
            return await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴍᴜᴛᴇ ʙᴏᴛ!")
        
        duration = Config.MUTE_DURATION
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ"
        
        await db.add_mute(target.id, chat.id, duration, reason, user.id)
        await context.bot.restrict_chat_member(chat.id, target.id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"🔇 <b>Mᴜᴛᴇᴅ {target.first_name}!</b>\n⏱️ {duration}s\n📝 {reason}", parse_mode=ParseMode.HTML)
        
        async def auto_unmute():
            await asyncio.sleep(duration)
            await db.remove_mute(target.id, chat.id)
            try:
                await context.bot.restrict_chat_member(chat.id, target.id, ChatPermissions(can_send_messages=True))
            except:
                pass
        asyncio.create_task(auto_unmute())

    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/unmute @username\n/unmute (user_id)\n/unmute (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        await db.remove_mute(target.id, update.effective_chat.id)
        await context.bot.restrict_chat_member(update.effective_chat.id, target.id, ChatPermissions(can_send_messages=True))
        await update.message.reply_text(f"🔊 <b>Uɴᴍᴜᴛᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/kick @username\n/kick (user_id)\n/kick (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        if target.is_bot:
            return await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴋɪᴄᴋ ʙᴏᴛ!")
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await context.bot.unban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"👢 <b>Kɪᴄᴋᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/ban @username\n/ban (user_id)\n/ban (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        if target.is_bot:
            return await update.message.reply_text("❌ Cᴀɴ'ᴛ ʙᴀɴ ʙᴏᴛ!")
        await context.bot.ban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"🚫 <b>Bᴀɴɴᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/unban @username\n/unban (user_id)\n/unban (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        await context.bot.unban_chat_member(update.effective_chat.id, target.id)
        await update.message.reply_text(f"✅ <b>Uɴʙᴀɴɴᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/approve @username\n/approve (user_id)\n/approve (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        await db.approve_user(target.id, update.effective_chat.id)
        await update.message.reply_text(f"✅ <b>Aᴘᴘʀᴏᴠᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    async def unapprove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text("⚠️ Pʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ, ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴏʀ ᴘʀᴏᴠɪᴅᴇ ᴀɴ ID!\n\nUsᴀɢᴇ:\n/unapprove @username\n/unapprove (user_id)\n/unapprove (ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ)")
        await db.unapprove_user(target.id, update.effective_chat.id)
        await update.message.reply_text(f"❌ <b>Uɴᴀᴘᴘʀᴏᴠᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)

    # ────═◈═─ ROLE COMMANDS ─═◈═────

    async def cofounder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._add_role(update, context, "Co-Founder")
    async def uncofounder_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._remove_role(update, context, "Co-Founder")
    async def mod_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._add_role(update, context, "Moderator")
    async def unmod_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._remove_role(update, context, "Moderator")
    async def muter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._add_role(update, context, "Muter")
    async def unmuter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._remove_role(update, context, "Muter")
    async def cleaner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._add_role(update, context, "Chat Cleaner")
    async def uncleaner_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._remove_role(update, context, "Chat Cleaner")
    async def helper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._add_role(update, context, "Helper")
    async def unhelper_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._remove_role(update, context, "Helper")
    async def free_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._add_role(update, context, "Free")
    async def unfree_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._remove_role(update, context, "Free")

    async def _add_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE, role: str):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text(f"⚠️ Usᴀɢᴇ: /{role.lower().replace(' ', '')} @ᴜsᴇʀ\nᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ!\n\nᴏʀ ᴜsᴇ ID: /{role.lower().replace(' ', '')} (user_id)")
        
        await db.set_user_role(target.id, update.effective_chat.id, role)
        await update.message.reply_text(f"✅ <b>{role}</b> ʀᴏʟᴇ ᴀᴅᴅᴇᴅ ᴛᴏ {target.first_name}!", parse_mode=ParseMode.HTML)

    async def _remove_role(self, update: Update, context: ContextTypes.DEFAULT_TYPE, role: str):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        
        target = await self._get_target_user(update, context)
        if not target:
            return await update.message.reply_text(f"⚠️ Usᴀɢᴇ: /un{role.lower().replace(' ', '')} @ᴜsᴇʀ\nᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ!\n\nᴏʀ ᴜsᴇ ID: /un{role.lower().replace(' ', '')} (user_id)")
        
        await db.remove_user_role(target.id, update.effective_chat.id)
        await update.message.reply_text(f"❌ <b>{role}</b> ʀᴏʟᴇ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ {target.first_name}!", parse_mode=ParseMode.HTML)

    # ────═◈═─ PIN COMMANDS ─═◈═────

    async def pin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
        await context.bot.pin_chat_message(update.effective_chat.id, update.message.reply_to_message.message_id, disable_notification=True)
        await update.message.reply_text("📌 <b>Pɪɴɴᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    async def unpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        await context.bot.unpin_chat_message(update.effective_chat.id)
        await update.message.reply_text("📌 <b>Uɴᴘɪɴɴᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    async def pinned_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        pinned = await context.bot.get_chat(update.effective_chat.id)
        if pinned.pinned_message:
            await update.message.reply_text(f"📌 <b>Pɪɴɴᴇᴅ:</b>\n{pinned.pinned_message.text[:200]}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("📌 <b>Nᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!</b>", parse_mode=ParseMode.HTML)

    async def editpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
        await context.bot.unpin_chat_message(update.effective_chat.id)
        await context.bot.pin_chat_message(update.effective_chat.id, update.message.reply_to_message.message_id, disable_notification=True)
        await update.message.reply_text("📌 <b>Pɪɴ ᴜᴘᴅᴀᴛᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    async def delpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        await context.bot.unpin_chat_message(update.effective_chat.id)
        await update.message.reply_text("🗑️ <b>Pɪɴ ᴅᴇʟᴇᴛᴇᴅ!</b>", parse_mode=ParseMode.HTML)

    # ────═◈═─ DELETE COMMANDS ─═◈═────

    async def del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
        try:
            await context.bot.delete_message(update.effective_chat.id, update.message.reply_to_message.message_id)
            await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)[:50]}", parse_mode=ParseMode.HTML)

    async def logdel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
        try:
            msg = update.message.reply_to_message
            await context.bot.delete_message(update.effective_chat.id, msg.message_id)
            await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
            await update.message.reply_text("✅ <b>Dᴇʟᴇᴛᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)[:50]}", parse_mode=ParseMode.HTML)

    async def purge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        
        user = update.effective_user
        chat = update.effective_chat
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                return await update.message.reply_text("❌ Aᴅᴍɪɴ ᴏɴʟʏ!")
        except:
            return
        
        if not update.message.reply_to_message:
            return await update.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴍᴇssᴀɢᴇ!")
        
        start_msg_id = update.message.reply_to_message.message_id
        current_msg_id = update.message.message_id
        deleted_count = 0
        
        for msg_id in range(current_msg_id, start_msg_id - 1, -1):
            try:
                await context.bot.delete_message(chat.id, msg_id)
                deleted_count += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
        
        if deleted_count > 0:
            await update.message.reply_text(f"🧹 <b>Pᴜʀɢᴇᴅ {deleted_count} ᴍᴇssᴀɢᴇs!</b>", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text("❌ Nᴏ ᴍᴇssᴀɢᴇs ᴄᴏᴜʟᴅ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ!\n⚠️ Mᴇssᴀɢᴇs ᴏʟᴅᴇʀ ᴛʜᴀɴ 48 ʜᴏᴜʀs ᴄᴀɴ'ᴛ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ.", parse_mode=ParseMode.HTML)

    # ────═◈═─ FILTER COMMANDS ─═◈═────

    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        if len(context.args) < 2:
            return await update.message.reply_text("⚠️ Usᴀɢᴇ: /filter ᴋᴇʏ ʀᴇᴘʟʏ")
        keyword = context.args[0].lower()
        reply = " ".join(context.args[1:])
        await db.add_filter(update.effective_chat.id, keyword, reply)
        await update.message.reply_text(f"✅ <b>Fɪʟᴛᴇʀ ᴀᴅᴅᴇᴅ!</b>\n<b>Kᴇʏ:</b> {keyword}", parse_mode=ParseMode.HTML)

    async def stopfilter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        if not context.args:
            return await update.message.reply_text("⚠️ Usᴀɢᴇ: /stopfilter ᴋᴇʏ")
        keyword = context.args[0].lower()
        result = await db.remove_filter(update.effective_chat.id, keyword)
        if result:
            await update.message.reply_text(f"✅ <b>Fɪʟᴛᴇʀ ʀᴇᴍᴏᴠᴇᴅ!</b>\n<b>Kᴇʏ:</b> {keyword}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"❌ Fɪʟᴛᴇʀ <b>{keyword}</b> ɴᴏᴛ ғᴏᴜɴᴅ!", parse_mode=ParseMode.HTML)

    async def filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return await update.message.reply_text("❌ Gʀᴏᴜᴘ ᴏɴʟʏ!")
        filters_list = await db.get_filters(update.effective_chat.id)
        if not filters_list:
            return await update.message.reply_text("📋 <b>Nᴏ ғɪʟᴛᴇʀs!</b>", parse_mode=ParseMode.HTML)
        text = f"📋 <b>Fɪʟᴛᴇʀs ({len(filters_list)})</b>\n\n"
        for f in filters_list:
            text += f"└ <b>{f['keyword']}</b>\n"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)

    async def filter_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        if not update.message or not update.message.text:
            return
        filters_list = await db.get_filters(update.effective_chat.id)
        text = update.message.text.lower()
        for f in filters_list:
            if f['keyword'].lower() in text:
                try:
                    await update.message.reply_text(f['reply_text'])
                except:
                    pass
                break

    # ────═◈═─ CALLBACK HANDLER ─═◈═────

    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
        
        try:
            if data == "main_menu":
                user = update.effective_user
                text = f"""
╔═══════════════════════════════════╗
║  ⚡ <b>PIKACHU PROTECTION BOT</b> ⚡
╚═══════════════════════════════════╝

✨ <b>Hᴇʟʟᴏ {user.first_name}!</b> ✨
💎 <b>Pʀᴇᴍɪᴜᴍ:</b> {'✅ Aᴄᴛɪᴠᴇ' if is_premium else '❌ Iɴᴀᴄᴛɪᴠᴇ'}
📌 <b>Aᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ!</b>
{self.get_owner_credit()}
"""
                keyboard = Keyboards.main_menu(is_premium)
                await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

            elif data == "stats":
                if user_id != Config.OWNER_ID:
                    return await query.answer("❌ Oɴʟʏ ᴏᴡɴᴇʀ!", show_alert=True)
                users = db.users.count_documents({})
                groups = db.groups.count_documents({})
                warns = db.warnings.count_documents({})
                mutes = db.mutes.count_documents({})
                text = f"""
📊 <b>Bᴏᴛ Sᴛᴀᴛs</b>
👥 Uꜱᴇʀs: {users}
📍 Gʀᴏᴜᴘs: {groups}
⚠️ Wᴀʀɴs: {warns}
🔇 Mᴜᴛᴇs: {mutes}
{self.get_owner_credit()}
"""
                keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
                await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

            elif data == "settings":
                keyboard = Keyboards.settings_menu()
                await query.edit_message_text("⚙️ <b>Sᴇᴛᴛɪɴɢs</b>", parse_mode=ParseMode.HTML, reply_markup=keyboard)

            elif data == "help":
                keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
                await query.edit_message_text("📖 <b>Usᴇ /help ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs</b>", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

            elif data == "about":
                keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
                await query.edit_message_text(f"⚡ <b>{Config.BOT_NAME}</b>\n👑 {Config.OWNER_NAME}", parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

            elif data == "staff":
                await query.edit_message_text("👥 Usᴇ /staff", parse_mode=ParseMode.HTML)

            elif data == "sg":
                await query.edit_message_text("🔄 Usᴇ /sg @user", parse_mode=ParseMode.HTML)

            elif data == "history":
                await query.edit_message_text("📜 Usᴇ /history @user", parse_mode=ParseMode.HTML)

            elif data == "chat":
                await query.edit_message_text("💬 Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ!", parse_mode=ParseMode.HTML)

            elif data == "roles":
                keyboard = Keyboards.role_keyboard()
                await query.edit_message_text("👑 <b>Rᴏʟᴇs</b>", parse_mode=ParseMode.HTML, reply_markup=keyboard)

            elif data.startswith("role_"):
                role = data.replace("role_", "").upper()
                await query.edit_message_text(f"👑 <b>{role}</b>", parse_mode=ParseMode.HTML)

            elif data.startswith("toggle_"):
                setting = data.replace("toggle_", "")
                chat_id = update.effective_chat.id
                settings = await db.get_settings(chat_id)
                current = settings.get(setting, True)
                await db.update_settings(chat_id, setting, not current)
                await query.edit_message_text(f"✅ <b>{setting.upper()}</b> {'Enabled' if not current else 'Disabled'}!", parse_mode=ParseMode.HTML)

            elif data == "premium":
                if is_premium:
                    text = "💎 <b>Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴇ!</b>"
                else:
                    text = f"💎 <b>Pʀᴇᴍɪᴜᴍ</b>\n💰 $5/ᴍᴏɴᴛʜ\n📞 {Config.OWNER_USERNAME}"
                keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
                await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

        except Exception as e:
            # If editing fails, try sending a new message
            try:
                await query.message.reply_text(
                    "❌ <b>Error processing request!</b>",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
            logger.error(f"Callback error: {e}")

    # ────═◈═─ ERROR HANDLER ─═◈═────

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        
        # Ignore common harmless errors
        error_str = str(context.error).lower()
        if any(x in error_str for x in ["there is no text", "message to edit", "message not found", "bad request"]):
            return
        
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"❌ <b>Error!</b>\n<code>{str(context.error)[:100]}</code>",
                    parse_mode=ParseMode.HTML
                )
        except:
            pass

    # ────═◈═─ RUN BOT ─═◈═────

    def run(self):
        try:
            self.app = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Register all command handlers
            self.app.add_handler(CommandHandler("start", self.start))
            self.app.add_handler(CommandHandler("help", self.help_command))
            self.app.add_handler(CommandHandler("about", self.about_command))
            self.app.add_handler(CommandHandler("ping", self.ping_command))
            self.app.add_handler(CommandHandler("staff", self.staff_command))
            self.app.add_handler(CommandHandler("info", self.info_command))
            self.app.add_handler(CommandHandler("infopvt", self.infopvt_command))
            self.app.add_handler(CommandHandler("me", self.me_command))
            self.app.add_handler(CommandHandler("geturl", self.geturl_command))
            self.app.add_handler(CommandHandler("sg", self.sg_command))
            self.app.add_handler(CommandHandler("history", self.history_command))
            self.app.add_handler(CommandHandler("chat", self.chat_command))
            self.app.add_handler(CommandHandler("roles", self.roles_command))
            self.app.add_handler(CommandHandler("premium", self.premium_command))
            self.app.add_handler(CommandHandler("enablewelcome", self.enable_welcome))
            self.app.add_handler(CommandHandler("disablewelcome", self.disable_welcome))
            self.app.add_handler(CommandHandler("settings", self.settings_command))
            self.app.add_handler(CommandHandler("reload", self.reload_command))
            
            # Lock Commands
            self.app.add_handler(CommandHandler("locktypes", self.locktypes_command))
            self.app.add_handler(CommandHandler("lock", self.lock_command))
            self.app.add_handler(CommandHandler("unlock", self.unlock_command))
            
            # Moderation Commands
            self.app.add_handler(CommandHandler("warn", self.warn_command))
            self.app.add_handler(CommandHandler("unwarn", self.unwarn_command))
            self.app.add_handler(CommandHandler("warns", self.warns_command))
            self.app.add_handler(CommandHandler("delwarn", self.delwarn_command))
            self.app.add_handler(CommandHandler("resetwarns", self.resetwarns_command))
            self.app.add_handler(CommandHandler("mute", self.mute_command))
            self.app.add_handler(CommandHandler("unmute", self.unmute_command))
            self.app.add_handler(CommandHandler("kick", self.kick_command))
            self.app.add_handler(CommandHandler("ban", self.ban_command))
            self.app.add_handler(CommandHandler("unban", self.unban_command))
            self.app.add_handler(CommandHandler("approve", self.approve_command))
            self.app.add_handler(CommandHandler("unapprove", self.unapprove_command))
            
            # Role Commands
            self.app.add_handler(CommandHandler("cofounder", self.cofounder_command))
            self.app.add_handler(CommandHandler("uncofounder", self.uncofounder_command))
            self.app.add_handler(CommandHandler("mod", self.mod_command))
            self.app.add_handler(CommandHandler("unmod", self.unmod_command))
            self.app.add_handler(CommandHandler("muter", self.muter_command))
            self.app.add_handler(CommandHandler("unmuter", self.unmuter_command))
            self.app.add_handler(CommandHandler("cleaner", self.cleaner_command))
            self.app.add_handler(CommandHandler("uncleaner", self.uncleaner_command))
            self.app.add_handler(CommandHandler("helper", self.helper_command))
            self.app.add_handler(CommandHandler("unhelper", self.unhelper_command))
            self.app.add_handler(CommandHandler("free", self.free_command))
            self.app.add_handler(CommandHandler("unfree", self.unfree_command))
            
            # Pin Commands
            self.app.add_handler(CommandHandler("pin", self.pin_command))
            self.app.add_handler(CommandHandler("unpin", self.unpin_command))
            self.app.add_handler(CommandHandler("pinned", self.pinned_command))
            self.app.add_handler(CommandHandler("editpin", self.editpin_command))
            self.app.add_handler(CommandHandler("delpin", self.delpin_command))
            
            # Delete Commands
            self.app.add_handler(CommandHandler("del", self.del_command))
            self.app.add_handler(CommandHandler("logdel", self.logdel_command))
            self.app.add_handler(CommandHandler("purge", self.purge_command))
            
            # Filter Commands
            self.app.add_handler(CommandHandler("filter", self.filter_command))
            self.app.add_handler(CommandHandler("stopfilter", self.stopfilter_command))
            self.app.add_handler(CommandHandler("filters", self.filters_command))
            
            # Callback handler
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            
            # Message handlers
            self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome_handler))
            self.app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, self.goodbye_handler))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.filter_handler))
            
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
