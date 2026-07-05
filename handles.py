from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ParseMode
import asyncio
import datetime
import re

from config import Config
from database import Database
from utils import Utils
from keyboards import Keyboards

db = Database()
utils = Utils()

class Handlers:
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Check premium status
        is_premium = await db.check_premium(user.id)
        
        # Add user to database
        await db.add_user(user.id, user.username, user.first_name)
        
        welcome_text = f"""
✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {Config.BOT_NAME}** ✨

────═◈═─ ✧◈✧ ─═◈═────
  🤖 ʙᴏᴛ: {Config.BOT_NAME}  
  👤 ᴜsᴇʀ: {user.first_name} 
  💎 ᴘʀᴇᴍɪᴜᴍ: { '✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ' } 
✦•····················•✦

🌟 **ғᴇᴀᴛᴜʀᴇs:**  
╰┈➤ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ  
╰┈➤ ᴀɴᴛɪ-sᴘᴀᴍ  
╰┈➤ ᴀɴᴛɪ-ʟɪɴᴋ  
╰┈➤ ᴡᴀʀɴ/ᴍᴜᴛᴇ/ʙᴀɴ/ᴋɪᴄᴋ  
╰┈➤ ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs  

👑 **ᴏᴡɴᴇʀ:**  
╰┈➤ {Config.OWNER_NAME} ({Config.OWNER_USERNAME})

📢 **ᴜsᴇ /help ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs**
"""
        
        keyboard = Keyboards.main_menu(is_premium)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
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
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new member join"""
        if not update.message.new_chat_members:
            return
        
        chat = update.effective_chat
        settings = await db.get_settings(chat.id)
        
        if not settings.get('welcome', True):
            return
        
        for member in update.message.new_chat_members:
            if member.is_bot:
                continue
            
            # Add user to db
            await db.add_user(member.id, member.username, member.first_name)
            
            # Get group info
            try:
                member_count = await context.bot.get_chat_member_count(chat.id)
            except:
                member_count = "?"
            
            welcome_msg = f"""
👋 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ {chat.title}!</b>

<b>ᴜsᴇʀ:</b> {member.first_name}
<b>ᴍᴇᴍʙᴇʀs:</b> {member_count}

🌟 <b>ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ {Config.BOT_NAME}</b>
"""
            
            # Send welcome message
            await context.bot.send_message(
                chat.id,
                welcome_msg,
                parse_mode=ParseMode.HTML
            )
    
    @staticmethod
    async def goodbye_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle member leaving"""
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
💔 <b>ɢᴏᴏᴅʙʏᴇ!</b> 💔

<b>ᴜsᴇʀ:</b> {member.first_name}
📍 <b>ɢʀᴏᴜᴘ:</b> {chat.title}

😢 ᴡᴇ ᴡɪʟʟ ᴍɪss ʏᴏᴜ!
"""
        await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode=ParseMode.HTML
        )
    
    @staticmethod
    async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warn command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
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
        
        if not target:
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ᴡᴀʀɴ ʙᴏᴛs!")
            return
        
        # Get reason
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        # Add warning
        await db.add_warning(target.id, chat.id, reason, user.id)
        
        # Get warning count
        warnings = await db.get_warnings(target.id, chat.id)
        warn_count = len(warnings)
        
        # Get settings
        settings = await db.get_settings(chat.id)
        max_warns = settings.get('warn_limit', 3)
        
        # Send warning message
        warn_msg = f"""
⚠️ <b>ᴡᴀʀɴɪɴɢ!</b> ⚠️

<b>ᴜsᴇʀ:</b> {target.first_name}
<b>ᴡᴀʀɴ:</b> {warn_count}/{max_warns}
<b>ʀᴇᴀsᴏɴ:</b> {reason}
"""
        
        await update.message.reply_text(warn_msg, parse_mode=ParseMode.HTML)
        
        # Check if user should be muted/banned
        if warn_count >= max_warns:
            await update.message.reply_text(f"⚠️ {target.first_name} ʜᴀs ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ! ᴛʜᴇʏ ᴡɪʟʟ ʙᴇ ᴍᴜᴛᴇᴅ.", parse_mode=ParseMode.HTML)
