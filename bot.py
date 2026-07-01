#!/usr/bin/env python3
"""
ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ - ᴘʀᴇᴍɪᴜᴍ ɢʀᴏᴜᴘ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ
"""

import logging
import sys
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from config import Config
from handlers import Handlers
from database import Database
from utils import Utils

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
    """Premium styled print message"""
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
        self.handlers = Handlers()
        
        # Premium startup message
        premium_print(f"ʙᴏᴛ ɪɴɪᴛɪᴀʟɪᴢɪɴɢ: {Config.BOT_NAME}", "🚀")
        premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
        premium_print(f"ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs: ʟᴏᴀᴅᴇᴅ", "💎")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
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
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Handle settings toggles
        if data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            status = "ᴇɴᴀʙʟᴇᴅ" if not current else "ᴅɪsᴀʙʟᴇᴅ"
            await query.edit_message_text(
                f"✅ **{setting.upper()}** {status}!",
                parse_mode="Markdown"
            )
            await asyncio.sleep(2)
            await query.edit_message_text(
                "⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**",
                reply_markup=Keyboards.settings_menu()
            )
        
        # Handle setting navigation
        elif data == "settings":
            await query.edit_message_text(
                "⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**\n\n"
                "ᴄʜᴏᴏsᴇ ᴀ sᴇᴛᴛɪɴɢ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:",
                reply_markup=Keyboards.settings_menu(),
                parse_mode="Markdown"
            )
        
        elif data == "back_main":
            is_premium = await db.check_premium(user_id)
            await query.edit_message_text(
                "🏠 **ᴍᴀɪɴ ᴍᴇɴᴜ**",
                reply_markup=Keyboards.main_menu(is_premium),
                parse_mode="Markdown"
            )
        
        elif data == "back_settings":
            await query.edit_message_text(
                "⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**\n\n"
                "ᴄʜᴏᴏsᴇ ᴀ sᴇᴛᴛɪɴɢ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ:",
                reply_markup=Keyboards.settings_menu(),
                parse_mode="Markdown"
            )
        
        # Handle specific settings
        elif data == "set_welcome":
            settings = await db.get_settings(chat_id)
            current = settings.get('welcome', True)
            await query.edit_message_text(
                f"👋 **ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ**\n\n"
                f"ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n\n"
                "ᴛᴏɢɢʟᴇ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ:",
                reply_markup=Keyboards.toggle_keyboard("welcome", current),
                parse_mode="Markdown"
            )
        
        elif data == "set_goodbye":
            settings = await db.get_settings(chat_id)
            current = settings.get('goodbye', True)
            await query.edit_message_text(
                f"👋 **ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ**\n\n"
                f"ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n\n"
                "ᴛᴏɢɢʟᴇ ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ:",
                reply_markup=Keyboards.toggle_keyboard("goodbye", current),
                parse_mode="Markdown"
            )
        
        elif data == "set_antispam":
            settings = await db.get_settings(chat_id)
            current = settings.get('antispam', True)
            await query.edit_message_text(
                f"🛡️ **ᴀɴᴛɪ-sᴘᴀᴍ**\n\n"
                f"ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n\n"
                "ᴛᴏɢɢʟᴇ ᴀɴᴛɪ-sᴘᴀᴍ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ:",
                reply_markup=Keyboards.toggle_keyboard("antispam", current),
                parse_mode="Markdown"
            )
        
        elif data == "set_antilink":
            settings = await db.get_settings(chat_id)
            current = settings.get('antilink', False)
            await query.edit_message_text(
                f"🔗 **ᴀɴᴛɪ-ʟɪɴᴋ**\n\n"
                f"ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs: {'✅ ᴇɴᴀʙʟᴇᴅ' if current else '❌ ᴅɪsᴀʙʟᴇᴅ'}\n\n"
                "ᴛᴏɢɢʟᴇ ᴀɴᴛɪ-ʟɪɴᴋ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ:",
                reply_markup=Keyboards.toggle_keyboard("antilink", current),
                parse_mode="Markdown"
            )
        
        elif data == "set_warnlimit":
            settings = await db.get_settings(chat_id)
            current = settings.get('warn_limit', 3)
            await query.edit_message_text(
                f"⚠️ **ᴡᴀʀɴ ʟɪᴍɪᴛ**\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ʟɪᴍɪᴛ: {current}\n\n"
                "sᴇʟᴇᴄᴛ ɴᴇᴡ ᴡᴀʀɴ ʟɪᴍɪᴛ:",
                reply_markup=Keyboards.warning_limit_keyboard(),
                parse_mode="Markdown"
            )
        
        elif data.startswith("set_warnlimit_"):
            limit = int(data.replace("set_warnlimit_", ""))
            await db.update_settings(chat_id, "warn_limit", limit)
            await query.edit_message_text(
                f"✅ **ᴡᴀʀɴ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ:** {limit if limit > 0 else '∞'}",
                parse_mode="Markdown"
            )
            await asyncio.sleep(2)
            await query.edit_message_text(
                "⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**",
                reply_markup=Keyboards.settings_menu()
            )
        
        elif data == "set_mutetime":
            settings = await db.get_settings(chat_id)
            current = settings.get('mute_duration', 300)
            await query.edit_message_text(
                f"🔇 **ᴍᴜᴛᴇ ᴅᴜʀᴀᴛɪᴏɴ**\n\n"
                f"ᴄᴜʀʀᴇɴᴛ ᴅᴜʀᴀᴛɪᴏɴ: {Utils.format_duration(current)}\n\n"
                "sᴇʟᴇᴄᴛ ɴᴇᴡ ᴍᴜᴛᴇ ᴅᴜʀᴀᴛɪᴏɴ:",
                reply_markup=Keyboards.mute_duration_keyboard(),
                parse_mode="Markdown"
            )
        
        elif data.startswith("set_mutetime_"):
            duration = int(data.replace("set_mutetime_", ""))
            await db.update_settings(chat_id, "mute_duration", duration)
            await query.edit_message_text(
                f"✅ **ᴍᴜᴛᴇ ᴅᴜʀᴀᴛɪᴏɴ sᴇᴛ ᴛᴏ:** {Utils.format_duration(duration)}",
                parse_mode="Markdown"
            )
            await asyncio.sleep(2)
            await query.edit_message_text(
                "⚙️ **sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ**",
                reply_markup=Keyboards.settings_menu()
            )
        
        # Premium features
        elif data == "premium":
            is_premium = await db.check_premium(user_id)
            if is_premium:
                await query.edit_message_text(
                    "💎 **ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs**\n\n"
                    "✅ ʏᴏᴜ ᴀʀᴇ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ!\n\n"
                    "**ᴜɴʟᴏᴄᴋᴇᴅ ғᴇᴀᴛᴜʀᴇs:**\n"
                    "╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ\n"
                    "╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ\n"
                    "╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ\n"
                    "╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs\n"
                    "╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ\n\n"
                    "✨ ᴛʜᴀɴᴋs ғᴏʀ ʙᴇɪɴɢ ᴘʀᴇᴍɪᴜᴍ!",
                    reply_markup=Keyboards.premium_keyboard(),
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    "💎 **ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ**\n\n"
                    "**ᴜɴʟᴏᴄᴋ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs:**\n"
                    "╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ\n"
                    "╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ\n"
                    "╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ\n"
                    "╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs\n"
                    "╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ\n\n"
                    "**ᴘʀɪᴄᴇ:** $5/ᴍᴏɴᴛʜ\n\n"
                    "ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ᴛᴏ ʙᴜʏ:",
                    reply_markup=Keyboards.premium_keyboard(),
                    parse_mode="Markdown"
                )
        
        elif data == "buy_premium":
            await query.edit_message_text(
                "💰 **ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ**\n\n"
                "ᴛᴏ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ, ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ:\n"
                f"└ {Config.OWNER_USERNAME}\n\n"
                "**ᴘʀɪᴄɪɴɢ:**\n"
                "╰┈➤ $5/ᴍᴏɴᴛʜ\n"
                "╰┈➤ $50/ʏᴇᴀʀ\n\n"
                "ᴘᴀʏᴍᴇɴᴛ ᴀᴄᴄᴇᴘᴛᴇᴅ:\n"
                "╰┈➤ ᴜsᴅᴛ (ᴛʀᴄ20)\n"
                "╰┈➤ ʙɪᴛᴄᴏɪɴ\n"
                "╰┈➤ ᴇᴛʜᴇʀᴇᴜᴍ",
                reply_markup=Keyboards.premium_keyboard(),
                parse_mode="Markdown"
            )
        
        elif data == "check_premium":
            is_premium = await db.check_premium(user_id)
            status = "✅ ᴀᴄᴛɪᴠᴇ" if is_premium else "❌ ɪɴᴀᴄᴛɪᴠᴇ"
            await query.edit_message_text(
                f"💎 **ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs**\n\n"
                f"sᴛᴀᴛᴜs: {status}\n\n"
                f"ᴜsᴇʀ: {update.effective_user.first_name}",
                reply_markup=Keyboards.premium_keyboard(),
                parse_mode="Markdown"
            )
        
        # Stats and About
        elif data == "stats":
            if user_id not in Config.OWNER_ID:
                await query.edit_message_text(
                    "❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!",
                    parse_mode="Markdown"
                )
                return
            
            users_count = db.users.count_documents({})
            groups_count = db.groups.count_documents({})
            warnings_count = db.warnings.count_documents({})
            mutes_count = db.mutes.count_documents({})
            premium_count = db.premium.count_documents({})
            
            stats_text = f"""
📊 **ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs** 📊

╔═══════════════════════════╗
║  👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {users_count}  ║
║  📍 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs: {groups_count} ║
║  ⚠️ ᴡᴀʀɴɪɴɢs: {warnings_count}   ║
║  🔇 ᴀᴄᴛɪᴠᴇ ᴍᴜᴛᴇs: {mutes_count} ║
║  💎 ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: {premium_count}║
╚═══════════════════════════╝

🔥 **ʙᴏᴛ ɪɴғᴏ:**
╰┈➤ ɴᴀᴍᴇ: {Config.BOT_NAME}
╰┈➤ ᴠᴇʀsɪᴏɴ: 2.0.0
╰┈➤ ᴏᴡɴᴇʀ: {Config.OWNER_NAME}

⚡ **sᴛᴀᴛᴜs:** ᴏɴʟɪɴᴇ
"""
            await query.edit_message_text(
                stats_text,
                parse_mode="Markdown",
                reply_markup=Keyboards.main_menu(False)
            )
        
        elif data == "about":
            about_text = f"""
⚡ **ᴀʙᴏᴜᴛ {Config.BOT_NAME}** ⚡

╔═══════════════════════════╗
║  🤖 ɴᴀᴍᴇ: {Config.BOT_NAME}  ║
║  📌 ɪᴅ: {Config.BOT_USERNAME} ║
║  👑 ᴏᴡɴᴇʀ: {Config.OWNER_NAME} ║
║  📞 ᴄᴏɴᴛᴀᴄᴛ: {Config.OWNER_USERNAME} ║
╚═══════════════════════════╝

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
"""
            await query.edit_message_text(
                about_text,
                parse_mode="Markdown",
                reply_markup=Keyboards.main_menu(False)
            )
        
        elif data == "help":
            help_text = """
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
╰┈➤ /settings - ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs  

**📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:**

╰┈➤ /start - sᴛᴀʀᴛ ʙᴏᴛ  
╰┈➤ /help - ɢᴇᴛ ʜᴇʟᴘ  
╰┈➤ /stats - ʙᴏᴛ sᴛᴀᴛs  
╰┈➤ /about - ᴀʙᴏᴜᴛ ʙᴏᴛ  

**💎 ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴍᴍᴀɴᴅs:**

╰┈➤ /premium - ᴄʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ  
╰┈➤ /activate - ᴀᴄᴛɪᴠᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ  

╚═══════════════════════════╝

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
            await query.edit_message_text(
                help_text,
                parse_mode="Markdown",
                reply_markup=Keyboards.main_menu(False)
            )
    
    async def antispam_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle anti-spam"""
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        # Check if antispam is enabled
        settings = await db.get_settings(chat.id)
        if not settings.get('antispam', True):
            return
        
        # Check if user is admin
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ['administrator', 'creator']:
                return
        except:
            return
        
        # Check for flooding
        if not context.user_data.get('last_message_time'):
            context.user_data['last_message_time'] = []
        
        # Add current time
        current_time = datetime.now().timestamp()
        context.user_data['last_message_time'].append(current_time)
        
        # Keep only last 10 messages
        if len(context.user_data['last_message_time']) > 10:
            context.user_data['last_message_time'] = context.user_data['last_message_time'][-10:]
        
        # Check if user is spamming
        if len(context.user_data['last_message_time']) >= 5:
            time_diff = current_time - context.user_data['last_message_time'][-5]
            if time_diff < 5:  # 5 messages in 5 seconds
                # Spam detected
                await context.bot.delete_message(chat.id, update.message.message_id)
                
                # Warn user
                warnings = await db.get_warnings(user.id, chat.id)
                warn_count = len(warnings)
                
                if warn_count < Config.MAX_WARNINGS:
                    await db.add_warning(user.id, chat.id, "sᴘᴀᴍᴍɪɴɢ", "ʙᴏᴛ")
                    warn_msg = Messages.WARN.format(
                        user_mention=utils.format_user_mention(user),
                        count=warn_count + 1,
                        max=Config.MAX_WARNINGS,
                        reason="sᴘᴀᴍᴍɪɴɢ"
                    )
                    await context.bot.send_message(
                        chat.id,
                        warn_msg,
                        parse_mode=ParseMode.HTML
                    )
                else:
                    # Auto mute
                    await db.add_mute(user.id, chat.id, Config.MUTE_DURATION, "ᴀᴜᴛᴏ-ᴍᴜᴛᴇ ғᴏʀ sᴘᴀᴍ", "ʙᴏᴛ")
                    await context.bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        ChatPermissions(can_send_messages=False)
                    )
                    mute_msg = Messages.MUTE.format(
                        user_mention=utils.format_user_mention(user),
                        duration=utils.format_duration(Config.MUTE_DURATION),
                        reason="sᴘᴀᴍᴍɪɴɢ"
                    )
                    await context.bot.send_message(
                        chat.id,
                        mute_msg,
                        parse_mode=ParseMode.HTML
                    )
    
    async def antilink_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle anti-link"""
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        # Check if antilink is enabled
        settings = await db.get_settings(chat.id)
        if not settings.get('antilink', False):
            return
        
        # Check if user is admin
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if member.status in ['administrator', 'creator']:
                return
        except:
            return
        
        # Check for links
        if utils.check_link(update.message.text):
            await context.bot.delete_message(chat.id, update.message.message_id)
            
            # Warn user
            await db.add_warning(user.id, chat.id, "sᴇɴᴅɪɴɢ ʟɪɴᴋs", "ʙᴏᴛ")
            
            warn_msg = f"""
⚠️ **ʟɪɴᴋ ᴅᴇᴛᴇᴄᴛᴇᴅ!** ⚠️

{utils.format_user_mention(user)}, 
ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ sᴇɴᴅ ʟɪɴᴋs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!

🚫 **ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ**
"""
            await context.bot.send_message(
                chat.id,
                warn_msg,
                parse_mode=ParseMode.HTML
            )
    
    def run(self):
        """Run the bot"""
        try:
            # Create application
            self.app = Application.builder().token(Config.BOT_TOKEN).build()
            
            # Add command handlers
            self.app.add_handler(CommandHandler("start", self.handlers.start))
            self.app.add_handler(CommandHandler("help", self.handlers.help_command))
            self.app.add_handler(CommandHandler("stats", self.handlers.stats_command))
            self.app.add_handler(CommandHandler("about", self.handlers.about_command))
            
            # Moderation commands
            self.app.add_handler(CommandHandler("warn", self.handlers.warn_command))
            self.app.add_handler(CommandHandler("warns", self.handlers.warns_command))
            self.app.add_handler(CommandHandler("resetwarns", self.handlers.reset_warns))
            self.app.add_handler(CommandHandler("mute", self.handlers.mute_command))
            self.app.add_handler(CommandHandler("unmute", self.handlers.unmute_command))
            self.app.add_handler(CommandHandler("kick", self.handlers.kick_command))
            self.app.add_handler(CommandHandler("ban", self.handlers.ban_command))
            self.app.add_handler(CommandHandler("unban", self.handlers.unban_command))
            
            # Add callback handler
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            
            # Add message handlers
            self.app.add_handler(MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS,
                self.handlers.welcome_handler
            ))
            self.app.add_handler(MessageHandler(
                filters.StatusUpdate.LEFT_CHAT_MEMBER,
                self.handlers.goodbye_handler
            ))
            self.app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.antispam_handler
            ))
            self.app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.antilink_handler
            ))
            
            # Add error handler
            self.app.add_error_handler(self.handlers.error_handler)
            
            # Premium startup messages
            premium_print(f"ʙᴏᴛ {Config.BOT_NAME} ɪs ɴᴏᴡ ʀᴜɴɴɪɴɢ!", "⚡")
            premium_print(f"ᴏᴡɴᴇʀ: {Config.OWNER_NAME}", "👑")
            premium_print(f"ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: {db.premium.count_documents({})}", "💎")
            premium_print(f"ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs: {db.groups.count_documents({})}", "📍")
            
            # Run the bot
            self.app.run_polling()
            
        except Exception as e:
            premium_print(f"ᴇʀʀᴏʀ: {str(e)}", "❌")
            sys.exit(1)

if __name__ == "__main__":
    # Check for required configurations
    if not Config.BOT_TOKEN:
        premium_print("ʙᴏᴛ ᴛᴏᴋᴇɴ ɴᴏᴛ ғᴏᴜɴᴅ! ᴘʟᴇᴀsᴇ sᴇᴛ ʙᴏᴛ_ᴛᴏᴋᴇɴ ɪɴ .ᴇɴᴠ ғɪʟᴇ", "❌")
        sys.exit(1)
    
    # Start the bot
    bot = PikachuProtectionBot()
    bot.run()
