from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ParseMode
import asyncio
import datetime
import re

from config import Config, Messages
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

╔═══════════════════════════╗
║  🤖 ʙᴏᴛ: {Config.BOT_NAME}  ║
║  👤 ᴜsᴇʀ: {user.first_name} ║
║  💎 ᴘʀᴇᴍɪᴜᴍ: { '✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ' } ║
╚═══════════════════════════╝

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
        
        # Premium extra text
        if is_premium:
            welcome_text += f"""
\n{Messages.PREMIUM_START.format(
    user_name=user.first_name,
    bot_name=Config.BOT_NAME
)}"""
        
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
            
            welcome_msg = Messages.WELCOME.format(
                user_mention=utils.format_user_mention(member),
                group_name=chat.title or "Group",
                member_count=member_count,
                bot_name=Config.BOT_NAME
            )
            
            # Send welcome message
            sent_msg = await context.bot.send_message(
                chat.id,
                welcome_msg,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            # Auto-delete welcome message after configured time
            if Config.WELCOME_DELETE_AFTER > 0:
                await asyncio.sleep(Config.WELCOME_DELETE_AFTER)
                try:
                    await sent_msg.delete()
                except:
                    pass
    
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
        
        goodbye_msg = Messages.GOODBYE.format(
            user_mention=utils.format_user_mention(member),
            group_name=chat.title or "Group"
        )
        
        sent_msg = await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode=ParseMode.HTML
        )
        
        # Auto-delete goodbye message
        await asyncio.sleep(30)
        try:
            await sent_msg.delete()
        except:
            pass
    
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
        
        if not context.args:
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
        warn_msg = Messages.WARN.format(
            user_mention=utils.format_user_mention(target),
            count=warn_count,
            max=max_warns,
            reason=reason
        )
        
        await update.message.reply_text(warn_msg, parse_mode=ParseMode.HTML)
        
        # Check if user should be muted/banned
        if warn_count >= max_warns:
            mute_duration = settings.get('mute_duration', Config.MUTE_DURATION)
            await db.add_mute(target.id, chat.id, mute_duration, f"ᴇxᴄᴇᴇᴅᴇᴅ ᴡᴀʀɴ ʟɪᴍɪᴛ ({max_warns})", user.id)
            
            try:
                await context.bot.restrict_chat_member(
                    chat.id,
                    target.id,
                    ChatPermissions(can_send_messages=False)
                )
                
                mute_msg = Messages.MUTE.format(
                    user_mention=utils.format_user_mention(target),
                    duration=utils.format_duration(mute_duration),
                    reason="ᴇxᴄᴇᴇᴅᴇᴅ ᴡᴀʀɴ ʟɪᴍɪᴛ"
                )
                await update.message.reply_text(mute_msg, parse_mode=ParseMode.HTML)
                
                # Auto-unmute after duration
                await asyncio.sleep(mute_duration)
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
                    unmute_msg = Messages.UNMUTE.format(
                        user_mention=utils.format_user_mention(target)
                    )
                    await context.bot.send_message(
                        chat.id,
                        unmute_msg,
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
                
            except Exception as e:
                await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warns command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        chat = update.effective_chat
        
        # Get target user
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
            await update.message.reply_text(
                f"✅ {utils.format_user_mention(target)} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs!",
                parse_mode=ParseMode.HTML
            )
            return
        
        warn_text = f"⚠️ **ᴡᴀʀɴɪɴɢs ғᴏʀ {utils.format_user_mention(target)}:**\n\n"
        for i, warn in enumerate(warnings, 1):
            warn_text += f"└ {i}. {warn['reason']} (ʙʏ ᴀᴅᴍɪɴ)\n"
        
        await update.message.reply_text(warn_text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def reset_warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resetwarns command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇsᴇᴛ ᴡᴀʀɴs!")
                return
        except:
            return
        
        # Get target user
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
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        await db.clear_warnings(target.id, chat.id)
        
        await update.message.reply_text(
            f"✅ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ ᴡᴀʀɴɪɴɢs ғᴏʀ {utils.format_user_mention(target)}!",
            parse_mode=ParseMode.HTML
        )
    
    @staticmethod
    async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mute command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴜᴛᴇ!")
                return
        except:
            return
        
        # Get target user
        target = None
        duration = Config.MUTE_DURATION
        reason = "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
            # Check for duration
            if len(context.args) > 1:
                try:
                    duration = utils.parse_duration(context.args[1])
                    if len(context.args) > 2:
                        reason = " ".join(context.args[2:])
                except:
                    reason = " ".join(context.args[1:])
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ᴍᴜᴛᴇ ʙᴏᴛs!")
            return
        
        # Add mute to database
        await db.add_mute(target.id, chat.id, duration, reason, user.id)
        
        try:
            await context.bot.restrict_chat_member(
                chat.id,
                target.id,
                ChatPermissions(can_send_messages=False)
            )
            
            mute_msg = Messages.MUTE.format(
                user_mention=utils.format_user_mention(target),
                duration=utils.format_duration(duration),
                reason=reason
            )
            await update.message.reply_text(mute_msg, parse_mode=ParseMode.HTML)
            
            # Auto-unmute after duration
            await asyncio.sleep(duration)
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
                unmute_msg = Messages.UNMUTE.format(
                    user_mention=utils.format_user_mention(target)
                )
                await context.bot.send_message(
                    chat.id,
                    unmute_msg,
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
                
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unmute command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇ!")
                return
        except:
            return
        
        # Get target user
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
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        # Remove mute from database
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
            
            unmute_msg = Messages.UNMUTE.format(
                user_mention=utils.format_user_mention(target)
            )
            await update.message.reply_text(unmute_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /kick command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴋɪᴄᴋ!")
                return
        except:
            return
        
        # Get target user
        target = None
        reason = "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
            if len(context.args) > 1:
                reason = " ".join(context.args[1:])
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ʙᴏᴛs!")
            return
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await context.bot.unban_chat_member(chat.id, target.id)
            
            kick_msg = Messages.KICK.format(
                user_mention=utils.format_user_mention(target),
                reason=reason
            )
            await update.message.reply_text(kick_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ban command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʙᴀɴ!")
                return
        except:
            return
        
        # Get target user
        target = None
        reason = "ɴᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
            if len(context.args) > 1:
                reason = " ".join(context.args[1:])
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ ᴄᴀɴ'ᴛ ʙᴀɴ ʙᴏᴛs!")
            return
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            
            ban_msg = Messages.BAN.format(
                user_mention=utils.format_user_mention(target),
                reason=reason
            )
            await update.message.reply_text(ban_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        # Check admin permission
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴ!")
                return
        except:
            return
        
        # Get target user
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
            await update.message.reply_text("⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        try:
            await context.bot.unban_chat_member(chat.id, target.id)
            
            unban_msg = Messages.UNBAN.format(
                user_mention=utils.format_user_mention(target)
            )
            await update.message.reply_text(unban_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ ᴇʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if update.effective_user.id not in Config.OWNER_ID:
            await update.message.reply_text("❌ ᴏɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        
        # Get stats from database
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
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
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
        
        await update.message.reply_text(about_text, parse_mode=ParseMode.HTML)
