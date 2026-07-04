#!/usr/bin/env python3
"""
ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ - ᴀʟʟ ɪɴ ᴏɴᴇ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ
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
        premium_print(f"ʙᴏᴛ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ: {Config.BOT_NAME}", "🚀")
        premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
        premium_print(f"ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs: ʟᴏᴀᴅᴇᴅ", "💎")

    # ────═◈═─ START COMMAND ─═◈═────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.add_user(user.id, user.username, user.first_name)
        
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        welcome_text = f"""
✨ **ʜᴇʟʟᴏ {user.first_name}!** ✨

👋 **ɪ ᴀᴍ {Config.BOT_NAME}** 🤖

**ʜɪɢʜʟɪɢʜᴛs:**
─────────────────────────────
- 🛡️ Sᴍᴀʀᴛ Aɴᴛɪ-Sᴘᴀᴍ & Lɪɴᴋ Sʜɪᴇʟᴅ
- 🔒 Aᴅᴀᴘᴛɪᴠᴇ Lᴏᴄᴋ Sʏsᴛᴇᴍ (URLs, Mᴇᴅɪᴀ, Lᴀɴɢᴜᴀɢᴇ & ᴍᴏʀᴇ)
- ⚙️ Mᴏᴅᴜʟᴀʀ & Sᴄᴀʟᴀʙʟᴇ Pʀᴏᴛᴇᴄᴛɪᴏɴ
- 🎨 Sʟᴇᴇᴋ UI ᴡɪᴛʜ Iɴʟɪɴᴇ Cᴏɴᴛʀᴏʟs
─────────────────────────────

» **ᴍᴏʀᴇ ɴᴇᴡ ғᴇᴀᴛᴜʀᴇs ᴄᴏᴍɪɴɢ sᴏᴏɴ ...**

💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs:** {'✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")],
            [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
            [InlineKeyboardButton("👥 sᴛᴀғғ", callback_data="staff")]
        ]
        if is_premium:
            keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
        
        photo_url = "https://i.ibb.co/7NT4SDXy/file-124.jpg"
        
        try:
            await update.message.reply_photo(
                photo=photo_url,
                caption=welcome_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await update.message.reply_text(
                welcome_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    # ────═◈═─ HELP COMMAND ─═◈═────
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

**👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /warn @user - ᴡᴀʀɴ ᴜsᴇʀ
╰┈➤ /warns @user - ᴄʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /resetwarns @user - ʀᴇsᴇᴛ ᴡᴀʀɴs
╰┈➤ /mute @user - ᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /unmute @user - ᴜɴᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /kick @user - ᴋɪᴄᴋ ᴜsᴇʀ
╰┈➤ /ban @user - ʙᴀɴ ᴜsᴇʀ
╰┈➤ /unban @user - ᴜɴʙᴀɴ ᴜsᴇʀ
╰┈➤ /approve @user - ᴀᴘᴘʀᴏᴠᴇ ᴜsᴇʀ ᴛᴏ sᴇɴᴅ ʟɪɴᴋs
╰┈➤ /unapprove @user - ʀᴇᴠᴏᴋᴇ ʟɪɴᴋ ᴀᴘᴘʀᴏᴠᴀʟ
╰┈➤ /setrules - sᴇᴛ ɢʀᴏᴜᴘ ʀᴜʟᴇs
╰┈➤ /rules - ᴠɪᴇᴡ ɢʀᴏᴜᴘ ʀᴜʟᴇs

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ
╰┈➤ /ping - ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛᴜs
╰┈➤ /premium - ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ PING COMMAND ─═◈═────
    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        start_time = datetime.now()
        msg = await update.message.reply_text("🏓 Pɪɴɢɪɴɢ...")
        end_time = datetime.now()
        latency = (end_time - start_time).microseconds / 1000
        await msg.edit_text(f"🏓 **ᴘᴏɴɢ!**\n\n⚡ Lᴀᴛᴇɴᴄʏ: `{latency:.2f}ms`\n🤖 Sᴛᴀᴛᴜs: ✅ ᴏɴʟɪɴᴇ", parse_mode="Markdown")

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
╰┈➤ {owner.first_name} (ᴏᴡɴᴇʀ)

👔 **ᴀᴅᴍɪɴs: ({len(admin_list)})**
"""
            for admin in admin_list:
                staff_text += f"╰┈➤ {admin.first_name}\n"
            
            staff_text += f"\n📊 **ᴛᴏᴛᴀʟ sᴛᴀғғ:** {len(admin_list) + 1}"
            
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            await update.message.reply_text(staff_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")

    # ────═◈═─ RULES COMMANDS ─═◈═────
    async def set_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ʀᴜʟᴇs!")
                return
        except:
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ʀᴜʟᴇs!\nᴇxᴀᴍᴘʟᴇ: `/setrules ɴᴏ sᴘᴀᴍ, ɴᴏ ᴀʙᴜsᴇ`")
            return
        
        rules = " ".join(context.args)
        await db.set_rules(chat.id, rules)
        await update.message.reply_text(f"✅ **ʀᴜʟᴇs sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!**\n\n📋 {rules}", parse_mode="Markdown")

    async def get_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        rules = await db.get_rules(chat.id)
        
        if rules:
            await update.message.reply_text(f"📋 **ɢʀᴏᴜᴘ ʀᴜʟᴇs:**\n\n{rules}", parse_mode="Markdown")
        else:
            await update.message.reply_text("ℹ️ ɴᴏ ʀᴜʟᴇs sᴇᴛ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.\nᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ʀᴜʟᴇs ᴜsɪɴɢ `/setrules`")

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
            
            try:
                member_count = await context.bot.get_chat_member_count(chat.id)
            except:
                member_count = "?"
            
            # ────═◈═─ GET USER DETAILS ─═◈═────
            try:
                user_full = await context.bot.get_chat(member.id)
                user_bio = getattr(user_full, 'bio', 'N/A')
                user_id = member.id
                user_name = member.first_name or "N/A"
                user_username = f"@{member.username}" if member.username else "N/A"
                
                # ────═◈═─ GET PROFILE PHOTO ─═◈═────
                photos = await context.bot.get_user_profile_photos(member.id, limit=1)
                photo_file_id = None
                if photos.total_count > 0:
                    photo_file_id = photos.photos[0][-1].file_id
                
                # ────═◈═─ GET RULES ─═◈═────
                rules = await db.get_rules(chat.id)
                rules_text = f"\n📋 **ʀᴜʟᴇs:**\n{rules}" if rules else ""
                
                # ────═◈═─ WELCOME MESSAGE ─═◈═────
                welcome_msg = f"""
✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴘᴀʀᴛʏ!** ✨

────═◈═─ ✧◈✧ ─═◈═────
👤 **ɴᴀᴍᴇ:** {user_name}
🆔 **ɪᴅ:** `{user_id}`
📛 **ᴜsᴇʀɴᴀᴍᴇ:** {user_username}
📝 **ʙɪᴏ:** {user_bio[:100] if user_bio != 'N/A' else 'N/A'}
────═◈═─ ✧◈✧ ─═◈═────
📍 **ɢʀᴏᴜᴘ:** {chat.title}
👥 **ᴍᴇᴍʙᴇʀs:** {member_count}
🔰 **ʀᴏʟᴇ:** { '👑 Oᴡɴᴇʀ' if member.id == chat.id else '👤 Mᴇᴍʙᴇʀ' }
{rules_text}
────═◈═─ ✧◈✧ ─═◈═────
🌟 **ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ {Config.BOT_NAME}** 🌟
"""
                
                # ────═◈═─ SEND WELCOME WITH PHOTO ─═◈═────
                if photo_file_id:
                    await context.bot.send_photo(
                        chat.id,
                        photo=photo_file_id,
                        caption=welcome_msg,
                        parse_mode="Markdown"
                    )
                else:
                    await context.bot.send_message(
                        chat.id,
                        welcome_msg,
                        parse_mode="Markdown"
                    )
                    
            except Exception as e:
                logger.error(f"Welcome handler error: {e}")
                # Fallback welcome
                fallback_msg = f"""
✨ **ᴡᴇʟᴄᴏᴍᴇ {member.first_name}!** ✨

📍 {chat.title}
👥 ᴍᴇᴍʙᴇʀs: {member_count}
🌟 ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ {Config.BOT_NAME}
"""
                await context.bot.send_message(
                    chat.id,
                    fallback_msg,
                    parse_mode="Markdown"
                )

    # ────═◈═─ GOODBYE HANDLER ─═◈═────
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
"""
        await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode="Markdown"
        )

    # ────═◈═─ ANTI-SPAM HANDLER ─═◈═────
    async def antispam_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        settings = await db.get_settings(chat.id)
        if not settings.get('antispam', True):
            return
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ['administrator', 'creator']:
                return
        except:
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

    # ────═◈═─ ANTI-LINK HANDLER ─═◈═────
    async def antilink_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        settings = await db.get_settings(chat.id)
        if not settings.get('antilink', False):
            return
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ['administrator', 'creator']:
                return
        except:
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

    # ────═◈═─ ANTI-18+ HANDLER ─═◈═────
    async def anti18_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        settings = await db.get_settings(chat.id)
        if not settings.get('anti18', True):
            return
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ['administrator', 'creator']:
                return
        except:
            return
        
        adult_keywords = ['porn', 'xxx', 'sex', 'nude', 'nsfw', '18+', 'adult']
        if any(keyword in update.message.text.lower() for keyword in adult_keywords):
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(
                f"🔞 **18+ ᴄᴏɴᴛᴇɴᴛ ᴅᴇᴛᴇᴄᴛᴇᴅ!**\n\n{user.first_name}, ᴛʜɪs ᴛʏᴘᴇ ᴏғ ᴄᴏɴᴛᴇɴᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ.",
                parse_mode="Markdown"
            )

    # ────═◈═─ MODERATION COMMANDS ─═◈═────
    
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
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
    
    # ────═◈═─ APPROVE/UNAPPROVE ─═◈═────
    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴘᴘʀᴏᴠᴇ!")
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
        
        await db.approve_user(target.id, chat.id)
        await update.message.reply_text(f"✅ **ᴀᴘᴘʀᴏᴠᴇᴅ** {target.first_name}!\n🔗 Nᴏᴡ ᴄᴀɴ sᴇɴᴅ ʟɪɴᴋs.", parse_mode="Markdown")

    async def unapprove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ!")
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
        
        await db.unapprove_user(target.id, chat.id)
        await update.message.reply_text(f"❌ **ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ** {target.first_name}!\n🔗 Nᴏ ᴍᴏʀᴇ ʟɪɴᴋs.", parse_mode="Markdown")

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
╰┈➤ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ
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
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

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

    # ────═◈═─ FIXED CALLBACK HANDLER ─═◈═────
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
                [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
                [InlineKeyboardButton("👥 sᴛᴀғғ", callback_data="staff")]
            ]
            if is_premium:
                keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
            
            try:
                await query.edit_message_text(
                    "🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    "🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        # ────═◈═─ STAFF ─═◈═────
        elif data == "staff":
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(
                    "👥 ᴜsᴇ /staff ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    "👥 ᴜsᴇ /staff ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
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

💫 **ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:**
ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ.

⚙️ **ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴀɴᴛɪ-ʟɪɴᴋ
╰┈➤ ᴀɴᴛɪ-18+
╰┈➤ ᴡᴀʀɴ sʏsᴛᴇᴍ
╰┈➤ ᴍᴜᴛᴇ/ᴜɴᴍᴜᴛᴇ
╰┈➤ ʙᴀɴ/ᴋɪᴄᴋ

📢 **ᴠᴇʀsɪᴏɴ:** 2.0.0
🔰 **sᴛᴀᴛᴜs:** ᴀᴄᴛɪᴠᴇ
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ HELP ─═◈═────
        elif data == "help":
            text = f"""
📖 **ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ** 📖

**👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /warn @user - ᴡᴀʀɴ ᴜsᴇʀ
╰┈➤ /warns @user - ᴄʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /resetwarns @user - ʀᴇsᴇᴛ ᴡᴀʀɴs
╰┈➤ /mute @user - ᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /unmute @user - ᴜɴᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /kick @user - ᴋɪᴄᴋ ᴜsᴇʀ
╰┈➤ /ban @user - ʙᴀɴ ᴜsᴇʀ
╰┈➤ /unban @user - ᴜɴʙᴀɴ ᴜsᴇʀ
╰┈➤ /approve @user - ᴀᴘᴘʀᴏᴠᴇ ᴜsᴇʀ
╰┈➤ /unapprove @user - ʀᴇᴠᴏᴋᴇ ᴀᴘᴘʀᴏᴠᴀʟ
╰┈➤ /setrules - sᴇᴛ ɢʀᴏᴜᴘ ʀᴜʟᴇs
╰┈➤ /rules - ᴠɪᴇᴡ ɢʀᴏᴜᴘ ʀᴜʟᴇs

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**
╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ
╰┈➤ /ping - ᴄʜᴇᴄᴋ ʙᴏᴛ
╰┈➤ /premium - ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
            keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ STATS ─═◈═────
        elif data == "stats":
            if user_id != Config.OWNER_ID:
                try:
                    await query.edit_message_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!", parse_mode="Markdown")
                except:
                    await query.message.reply_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!", parse_mode="Markdown")
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
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ SETTINGS ─═◈═────
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 ᴀɴᴛɪ-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
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
            try:
                await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ SETTINGS TOGGLES ─═◈═────
        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            try:
                await query.edit_message_text(f"✅ **{setting.upper()}** {'ᴇɴᴀʙʟᴇᴅ' if not current else 'ᴅɪsᴀʙʟᴇᴅ'}!", parse_mode="Markdown")
            except:
                await query.message.reply_text(f"✅ **{setting.upper()}** {'ᴇɴᴀʙʟᴇᴅ' if not current else 'ᴅɪsᴀʙʟᴇᴅ'}!", parse_mode="Markdown")
            
            await asyncio.sleep(1)
            
            keyboard = [
                [InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 ᴀɴᴛɪ-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text("⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        
        # ────═◈═─ SETTINGS OPTIONS ─═◈═────
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
                    f"{display_name}\n\nᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
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
            self.app.add_handler(CommandHandler("ping", self.ping_command))
            self.app.add_handler(CommandHandler("staff", self.staff_command))
            self.app.add_handler(CommandHandler("stats", self.stats_command))
            self.app.add_handler(CommandHandler("setrules", self.set_rules))
            self.app.add_handler(CommandHandler("rules", self.get_rules))
            
            # Moderation commands
            self.app.add_handler(CommandHandler("warn", self.warn_command))
            self.app.add_handler(CommandHandler("warns", self.warns_command))
            self.app.add_handler(CommandHandler("resetwarns", self.reset_warns))
            self.app.add_handler(CommandHandler("mute", self.mute_command))
            self.app.add_handler(CommandHandler("unmute", self.unmute_command))
            self.app.add_handler(CommandHandler("kick", self.kick_command))
            self.app.add_handler(CommandHandler("ban", self.ban_command))
            self.app.add_handler(CommandHandler("unban", self.unban_command))
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
