#!/usr/bin/env python3
"""
⚡ PIKACHU X PROTECTION BOT - ULTIMATE GROUP MANAGEMENT ⚡
More Powerful Than RoseBot
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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, User
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
LOG_CHANNEL = -1003424504397  # Your log channel

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

    async def log_action(self, chat_id, message):
        if self.log_channel:
            try:
                await self.app.bot.send_message(self.log_channel, message, parse_mode="HTML")
            except:
                pass

    def get_footer(self):
        return f"\n\n╰┈➤ <b>Created by {Config.OWNER_NAME}</b>"

    def get_owner_credit(self):
        return f"\n\n<b>👑 Created by: {Config.OWNER_NAME}</b>"

    # ────═◈═─ USER HISTORY TRACKING ─═◈═────
    async def track_user_history(self, user: User):
        """Track user's name and username changes"""
        try:
            # Get current user data
            current_data = {
                'first_name': user.first_name,
                'last_name': user.last_name or '',
                'username': user.username,
                'timestamp': datetime.now().isoformat()
            }
            
            # Get previous history
            history = await db.get_user_history(user.id)
            
            # Check for changes
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
                # Log the change
                change_msg = f"""
🔄 <b>USER PROFILE UPDATE</b>

👤 <b>User:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>New Username:</b> @{user.username if user.username else 'None'}
📝 <b>New Name:</b> {user.first_name}

📊 <b>Total Changes:</b> {len(await db.get_user_history(user.id))}
"""
                await self.log_action(None, change_msg)
                
        except Exception as e:
            logger.error(f"Error tracking user history: {e}")

    # ────═◈═─ SG COMMAND (User History) ─═◈═────
    async def sg_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's complete history (SG - User History Tracking)"""
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
        
        if not target:
            await update.message.reply_text("❌ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        # Get user history
        history = await db.get_user_history(target.id)
        user_stats = await db.get_user_stats(target.id)
        
        if not history:
            msg = f"""
📋 <b>HISTORY FOR {target.id}</b>

<b>Names</b>
No history recorded yet!

<b>Usernames</b>
No history recorded yet!

{self.get_footer()}
"""
            await update.message.reply_text(msg, parse_mode="HTML")
            return
        
        # Separate names and usernames
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
        
        # Build the message
        msg = f"""
📋 <b>HISTORY FOR {target.id}</b>

<b>Names</b>
"""
        
        # Add names (numbered)
        for i, entry in enumerate(names, 1):
            msg += f"{i:02d}. {entry['timestamp']} {entry['name']}\n"
        
        msg += f"\n<b>Usernames</b>\n"
        
        # Add usernames (numbered)
        if usernames:
            for i, entry in enumerate(usernames, 1):
                username_display = entry['username'] if entry['username'] else '(empty)'
                msg += f"{i}. {entry['timestamp']} {username_display}\n"
        else:
            msg += "No username history recorded!\n"
        
        # Add stats
        msg += f"\n📊 <b>Total Name Changes:</b> {len(names)}"
        msg += f"\n📊 <b>Total Username Changes:</b> {len(usernames)}"
        msg += f"\n📊 <b>Total Messages:</b> {user_stats.get('messages', 0)}"
        
        msg += self.get_footer()
        
        await update.message.reply_text(msg, parse_mode="HTML")

    # ────═◈═─ MAIN MENU MESSAGE ─═◈═────
    async def get_main_menu_message(self, user, is_premium):
        user_stats = await db.get_user_stats(user.id)
        history_count = len(await db.get_user_history(user.id))
        
        return f"""
⚡ <b>ᴘɪᴋᴀᴄʜᴜ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ʙᴏᴛ</b> ⚡

✨ <b>ʜᴇʟʟᴏ {user.first_name}!</b> ✨

ɪ ᴀᴍ ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ!

<b>📊 ʏᴏᴜʀ sᴛᴀᴛs:</b>
╰┈➤ 👥 ɢʀᴏᴜᴘs: {user_stats.get('groups', 0)}
╰┈➤ 🔄 ɴᴀᴍᴇ ᴄʜᴀɴɢᴇs: {history_count}
╰┈➤ 📝 ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs: {user_stats.get('messages', 0)}

<b>🔰 ᴘᴏᴡᴇʀғᴜʟ ғᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ 🛡️ Aɴᴛɪ-sᴘᴀᴍ & Lɪɴᴋ Sʜɪᴇʟᴅ
╰┈➤ ⚠️ Wᴀʀɴ/Mᴜᴛᴇ/Bᴀɴ/Kɪᴄᴋ
╰┈➤ 📌 Pɪɴ/Uɴᴘɪɴ/Dᴇʟᴇᴛᴇ/Pᴜʀɢᴇ
╰┈➤ 👋 Cᴜsᴛᴏᴍ Wᴇʟᴄᴏᴍᴇ/Gᴏᴏᴅʙʏᴇ
╰┈➤ 📊 Sᴛᴀғғ Lɪsᴛ & Sᴛᴀᴛs
╰┈➤ 📋 Cᴜsᴛᴏᴍ Rᴜʟᴇs
╰┈➤ 🔄 SG (User History Tracking)
╰┈➤ 📜 Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ
╰┈➤ 💬 Sᴍᴀʀᴛ Cʜᴀᴛ Rᴇsᴘᴏɴsᴇs
╰┈➤ 💎 Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs

💎 <b>ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs:</b> {'✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}

📌 <b>ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ!</b>
{self.get_owner_credit()}
"""

    # ────═◈═─ START COMMAND ─═◈═────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await db.add_user(user.id, user.username, user.first_name)
        await self.track_user_history(user)
        
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        welcome_text = await self.get_main_menu_message(user, is_premium)
        
        keyboard = [
            [InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")],
            [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
            [InlineKeyboardButton("👥 sᴛᴀғғ", callback_data="staff"), InlineKeyboardButton("🔄 SG", callback_data="sg")],
            [InlineKeyboardButton("📜 ʜɪsᴛᴏʀʏ", callback_data="history"), InlineKeyboardButton("💬 ᴄʜᴀᴛ", callback_data="chat")]
        ]
        if is_premium:
            keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
        
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

    # ────═◈═─ UPDATED WELCOME HANDLER ─═◈═────
    async def welcome_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.new_chat_members:
            return
        
        chat = update.effective_chat
        chat_id = chat.id
        chat_title = chat.title or "Unknown Group"
        
        logger.info(f"Welcome handler triggered in {chat_title} ({chat_id})")
        
        try:
            settings = await db.get_settings(chat_id)
            if not settings.get('welcome', True):
                logger.info(f"Welcome disabled for {chat_title}")
                return
        except Exception as e:
            logger.error(f"Error getting settings for {chat_id}: {e}")
        
        for member in update.message.new_chat_members:
            if member.is_bot:
                continue
            
            try:
                await db.add_user(member.id, member.username, member.first_name)
                await self.track_user_history(member)
                logger.info(f"Processing new member: {member.first_name} ({member.id})")
                
                # Get member count
                try:
                    member_count = await context.bot.get_chat_member_count(chat_id)
                except:
                    member_count = "?"
                
                # Get user details
                try:
                    user_full = await context.bot.get_chat(member.id)
                    user_bio = getattr(user_full, 'bio', 'No bio set')
                    user_name = member.first_name or "N/A"
                    user_username = f"@{member.username}" if member.username else "No username"
                except Exception as e:
                    logger.error(f"Error getting user details: {e}")
                    user_name = member.first_name or "N/A"
                    user_username = "No username"
                    user_bio = "No bio set"
                
                # Get profile photo
                photo_file_id = None
                try:
                    photos = await context.bot.get_user_profile_photos(member.id, limit=1)
                    if photos.total_count > 0:
                        photo_file_id = photos.photos[0][-1].file_id
                except Exception as e:
                    logger.warning(f"Could not fetch profile photo: {e}")
                
                # Get role
                role = "👤 Member"
                try:
                    chat_member = await context.bot.get_chat_member(chat_id, member.id)
                    if chat_member.status == 'creator':
                        role = "👑 Owner"
                    elif chat_member.status == 'administrator':
                        role = "👔 Admin"
                except:
                    pass
                
                # Build welcome message
                welcome_msg = f"""
<b>WELCOME TO THE PARTY!</b>

<b>NAME:</b> <code>{user_name}</code>
<b>ID:</b> <code>{member.id}</code>
<b>USERNAME:</b> <code>{user_username}</code>
<b>BIO:</b> <i>{user_bio[:100] if user_bio != 'No bio set' else 'No bio set'}</i>

<b>GROUP:</b> {chat_title}
<b>TOTAL MEMBERS:</b> {member_count}
<b>STATUS:</b> {role}

You won't leave me, right...?
I'm not a human...
{self.get_owner_credit()}
"""
                
                # Send welcome
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
                    simple_msg = f"<b>WELCOME TO THE PARTY!</b>\n\n<b>NAME:</b> <code>{member.first_name}</code>\n\nYou won't leave me, right...?{self.get_owner_credit()}"
                    await context.bot.send_message(chat_id, simple_msg, parse_mode="HTML")
                    
            except Exception as e:
                logger.error(f"Error processing member {member.id}: {e}")

    # ────═◈═─ HISTORY COMMAND ─═◈═────
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's complete change history"""
        chat = update.effective_chat
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        if not target:
            await update.message.reply_text("❌ User not found!")
            return
        
        history = await db.get_user_history(target.id)
        
        if not history:
            await update.message.reply_text(f"📜 No history found for {target.first_name}!", parse_mode="HTML")
            return
        
        # Send history as a file if too long
        if len(history) > 50:
            # Create a text file
            history_text = f"USER HISTORY FOR {target.first_name} (ID: {target.id})\n"
            history_text += "=" * 50 + "\n\n"
            
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', 'Unknown')
                name = entry.get('first_name', 'Unknown')
                username = entry.get('username', 'None')
                history_text += f"{i}. {timestamp}\n   Name: {name}\n   Username: @{username}\n\n"
            
            history_text += self.get_owner_credit()
            
            # Send as file
            with open(f"history_{target.id}.txt", "w", encoding="utf-8") as f:
                f.write(history_text)
            
            with open(f"history_{target.id}.txt", "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"history_{target.id}.txt",
                    caption=f"📜 Full history for {target.first_name}"
                )
            
            os.remove(f"history_{target.id}.txt")
        else:
            # Send as message
            msg = f"📜 <b>HISTORY FOR {target.first_name}</b>\n\n"
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', 'Unknown')
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
                name = entry.get('first_name', 'Unknown')
                username = entry.get('username', 'None')
                msg += f"{i}. {timestamp}\n   👤 {name}\n   📛 @{username}\n\n"
            
            msg += self.get_owner_credit()
            await update.message.reply_text(msg, parse_mode="HTML")

    # ────═◈═─ CHAT COMMAND ─═◈═────
    async def chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Interactive chat with the bot"""
        await update.message.reply_text(
            f"💬 <b>Chat with me!</b>\n\n"
            f"Send me any message and I'll respond!\n"
            f"Try asking me about:\n"
            f"• Your info\n"
            f"• Group stats\n"
            f"• Commands\n"
            f"• Anything else!{self.get_owner_credit()}",
            parse_mode="HTML"
        )

    # ────═◈═─ SMART CHAT HANDLER ─═◈═────
    async def smart_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle chat messages with smart responses"""
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        text = update.message.text.lower()
        
        # Track user messages
        await db.increment_user_messages(user.id, chat.id)
        
        # Smart responses
        responses = {
            'hi': f"👋 Hello {user.first_name}! How can I help you?",
            'hello': f"👋 Hi {user.first_name}! Nice to see you!",
            'hey': f"👋 Hey {user.first_name}! What's up?",
            'how are you': f"🤖 I'm great! Thanks for asking, {user.first_name}!",
            'who are you': f"🤖 I'm Pikachu Protection Bot, the ultimate group management bot!",
            'what is your name': f"🤖 My name is {Config.BOT_NAME}!",
            'thank you': f"🙌 You're welcome, {user.first_name}!",
            'thanks': f"🙌 No problem, {user.first_name}!",
            'goodbye': f"👋 Goodbye, {user.first_name}! See you later!",
            'bye': f"👋 Bye {user.first_name}! Have a great day!",
            'help': f"📖 Use /help to see all commands!",
            'info': f"📊 Use /info to get user information!",
            'ping': f"🏓 Use /ping to check bot status!",
            'love you': f"❤️ Love you too, {user.first_name}!",
            'i love you': f"❤️ I love you too, {user.first_name}!",
            'you are best': f"🌟 Thank you, {user.first_name}! You're the best!",
            'good bot': f"🤖 Thank you, {user.first_name}! I try my best!",
            'bad bot': f"😢 I'm sorry, {user.first_name}! I'll try harder!",
        }
        
        # Check for responses
        for key, response in responses.items():
            if key in text:
                await update.message.reply_text(response + self.get_owner_credit(), parse_mode="HTML")
                return
        
        # Check if user is asking about their info
        if 'my' in text and ('info' in text or 'id' in text or 'details' in text):
            info = f"""
📋 <b>Your Information</b>

👤 <b>Name:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>Username:</b> @{user.username if user.username else 'None'}
📊 <b>Messages:</b> {await db.get_user_message_count(user.id)}
{self.get_owner_credit()}
"""
            await update.message.reply_text(info, parse_mode="HTML")
            return
        
        # Check if user is asking about group
        if 'group' in text and ('info' in text or 'stats' in text):
            try:
                member_count = await context.bot.get_chat_member_count(chat.id)
                admins = await context.bot.get_chat_administrators(chat.id)
                
                group_info = f"""
📊 <b>Group Information</b>

📍 <b>Name:</b> {chat.title}
👥 <b>Members:</b> {member_count}
👔 <b>Admins:</b> {len(admins)}
🆔 <b>ID:</b> <code>{chat.id}</code>
{self.get_owner_credit()}
"""
                await update.message.reply_text(group_info, parse_mode="HTML")
                return
            except:
                pass

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
💔 <b>ɢᴏᴏᴅʙʏᴇ!</b> 💔

<b>ɴᴀᴍᴇ:</b> {member.first_name}
📍 <b>ɢʀᴏᴜᴘ:</b> {chat.title}

😢 ᴡᴇ ᴡɪʟʟ ᴍɪss ʏᴏᴜ!
{self.get_owner_credit()}
"""
        await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode="HTML"
        )

    # ────═◈═─ HELP COMMAND ─═◈═────
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""
📖 <b>ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ</b> 📖

╔═══════════════════════════════════════╗

<b>👑 ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b>

╰┈➤ /warn @user - ᴡᴀʀɴ ᴜsᴇʀ
╰┈➤ /unwarn @user - ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴ
╰┈➤ /warns @user - ᴄʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /delwarn - ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ & ᴡᴀʀɴ
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
╰┈➤ /filter ᴋᴇʏᴡᴏʀᴅ ʀᴇᴘʟʏ - ᴀᴅᴅ ᴀ ғɪʟᴛᴇʀ
╰┈➤ /stopfilter ᴋᴇʏᴡᴏʀᴅ - ʀᴇᴍᴏᴠᴇ ᴀ ғɪʟᴛᴇʀ
╰┈➤ /filters - ʟɪsᴛ ᴀʟʟ ғɪʟᴛᴇʀs
╰┈➤ /enablewelcome - ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ
╰┈➤ /disablewelcome - ᴅɪsᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ

<b>📊 ɢᴇɴᴇʀᴀʟ ᴄᴏᴍᴍᴀɴᴅs:</b>

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
╰┈➤ /sg @user - ᴠɪᴇᴡ ᴜsᴇʀ ʜɪsᴛᴏʀʏ (SG)
╰┈➤ /history @user - ᴠɪᴇᴡ ғᴜʟʟ ʜɪsᴛᴏʀʏ
╰┈➤ /chat - ᴄʜᴀᴛ ᴡɪᴛʜ ʙᴏᴛ

<b>🔰 ᴍᴏᴅᴇʀᴀᴛᴏʀ ᴄᴏᴍᴍᴀɴᴅs:</b>

╰┈➤ /reload - ᴜᴘᴅᴀᴛᴇ ᴀᴅᴍɪɴs ʟɪsᴛ
╰┈➤ /kick - ᴋɪᴄᴋ ᴜsᴇʀ
╰┈➤ /mute - ᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /warn - ᴡᴀʀɴ ᴜsᴇʀ

╚═══════════════════════════════════════╝

🔥 <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}</b>
{self.get_owner_credit()}
"""
        keyboard = [[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ FILTER COMMANDS ─═◈═────
    async def add_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can add filters!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/filter keyword reply text`\n\nExample: `/filter hello Hi there!`")
            return
        
        args = " ".join(context.args).split(" ", 1)
        if len(args) < 2:
            await update.message.reply_text("⚠️ Please provide a keyword and reply text!")
            return
        
        keyword = args[0].lower()
        reply_text = args[1]
        
        await db.add_filter(chat.id, keyword, reply_text)
        await update.message.reply_text(f"✅ <b>Filter added!</b>\n\n📌 <b>Keyword:</b> <code>{keyword}</code>\n📝 <b>Reply:</b> {reply_text}{self.get_owner_credit()}", parse_mode="HTML")

    async def remove_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can remove filters!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Usage: `/stopfilter keyword`")
            return
        
        keyword = context.args[0].lower()
        await db.remove_filter(chat.id, keyword)
        await update.message.reply_text(f"✅ <b>Filter removed!</b>\n\n📌 <b>Keyword:</b> <code>{keyword}</code>{self.get_owner_credit()}", parse_mode="HTML")

    async def list_filters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat = update.effective_chat
        filters = await db.get_filters(chat.id)
        
        if not filters:
            await update.message.reply_text(f"ℹ️ <b>No filters set in this group!</b>\n\nUse `/filter keyword reply` to add one.{self.get_owner_credit()}", parse_mode="HTML")
            return
        
        filter_text = "📋 <b>Active Filters:</b>\n\n"
        for f in filters:
            filter_text += f"├ <b>{f['keyword']}</b> → {f['reply_text'][:50]}...\n"
        
        filter_text += f"\n📊 <b>Total:</b> {len(filters)} filters"
        filter_text += self.get_owner_credit()
        
        await update.message.reply_text(filter_text, parse_mode="HTML")

    async def filter_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        if await self.is_admin(context, chat.id, user.id):
            return
        
        text = update.message.text.lower()
        filters = await db.get_filters(chat.id)
        
        for f in filters:
            if f['keyword'] in text:
                await update.message.reply_text(f['reply_text'] + self.get_owner_credit(), parse_mode="HTML")
                break

    # ────═◈═─ GET URL COMMAND ─═◈═────
    async def geturl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please reply to a message to get its link!")
            return
        
        chat = update.effective_chat
        msg = update.message.reply_to_message
        link = f"https://t.me/{chat.username}/{msg.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{msg.message_id}"
        await update.message.reply_text(f"🔗 <b>Message Link:</b>\n{link}{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ INFO COMMAND ─═◈═────
    async def info_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        if not target:
            await update.message.reply_text("❌ User not found!")
            return
        
        try:
            user_full = await context.bot.get_chat(target.id)
            bio = getattr(user_full, 'bio', 'No bio set')
            history_count = len(await db.get_user_history(target.id))
            msg_count = await db.get_user_message_count(target.id)
            
            info_text = f"""
📋 <b>User Information</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Name:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📛 <b>Username:</b> @{target.username if target.username else 'None'}
📝 <b>Bio:</b> {bio[:100] if bio != 'No bio set' else 'No bio set'}
📊 <b>Messages:</b> {msg_count}
🔄 <b>Name Changes:</b> {history_count}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
            await update.message.reply_text(info_text, parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def infopvt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        if not target:
            await update.message.reply_text("❌ User not found!")
            return
        
        try:
            user_full = await context.bot.get_chat(target.id)
            bio = getattr(user_full, 'bio', 'No bio set')
            history_count = len(await db.get_user_history(target.id))
            msg_count = await db.get_user_message_count(target.id)
            
            info_text = f"""
📋 <b>User Information</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Name:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📛 <b>Username:</b> @{target.username if target.username else 'None'}
📝 <b>Bio:</b> {bio[:100] if bio != 'No bio set' else 'No bio set'}
📊 <b>Messages:</b> {msg_count}
🔄 <b>Name Changes:</b> {history_count}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
            await context.bot.send_message(update.effective_user.id, info_text, parse_mode="HTML")
            await update.message.reply_text(f"✅ <b>Information sent in private!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ ME COMMAND ─═◈═────
    async def me_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat = update.effective_chat
        
        warnings = await db.get_warnings(user.id, chat.id)
        rules = await db.get_rules(chat.id)
        history_count = len(await db.get_user_history(user.id))
        msg_count = await db.get_user_message_count(user.id)
        
        me_text = f"""
📋 <b>Your Information</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Name:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>Username:</b> @{user.username if user.username else 'None'}
⚠️ <b>Warnings:</b> {len(warnings)}
📊 <b>Messages:</b> {msg_count}
🔄 <b>Name Changes:</b> {history_count}
📋 <b>Rules:</b> {rules[:100] if rules else 'No rules set'}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
        await update.message.reply_text(me_text, parse_mode="HTML")

    # ────═◈═─ PIN COMMANDS ─═◈═────
    async def pin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can pin messages!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please reply to a message to pin!")
            return
        
        try:
            await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
            await update.message.reply_text(f"📌 <b>Pinned!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"📌 <b>Pinned</b> by {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def unpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can unpin messages!")
            return
        
        try:
            await context.bot.unpin_chat_message(chat.id)
            await update.message.reply_text(f"📌 <b>Unpinned!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"📌 <b>Unpinned</b> by {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def pinned_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        try:
            pinned = await context.bot.get_chat(chat.id)
            if pinned.pinned_message:
                link = f"https://t.me/{chat.username}/{pinned.pinned_message.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{pinned.pinned_message.message_id}"
                await update.message.reply_text(f"📌 <b>Current Pinned Message:</b>\n{link}{self.get_owner_credit()}", parse_mode="HTML")
            else:
                await update.message.reply_text(f"📌 <b>No pinned message!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except:
            await update.message.reply_text(f"❌ Unable to fetch pinned message!{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ DELETE/PURGE COMMANDS ─═◈═────
    async def del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can delete messages!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please reply to a message to delete!")
            return
        
        try:
            await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await self.log_action(chat.id, f"🗑️ <b>Deleted</b> by {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def logdel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can use this command!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please reply to a message!")
            return
        
        msg = update.message.reply_to_message
        try:
            log_msg = f"""
🗑️ <b>Log Deleted Message</b>

📝 <b>Content:</b> {msg.text if msg.text else 'Media'}
👤 <b>User:</b> {msg.from_user.first_name}
🆔 <b>ID:</b> <code>{msg.from_user.id}</code>
👮 <b>By:</b> {user.first_name}
📍 <b>Group:</b> {chat.title}
"""
            await self.log_action(chat.id, log_msg)
            await context.bot.delete_message(chat.id, msg.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(f"✅ <b>Deleted and logged!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def purge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can purge messages!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please reply to a message to purge from!")
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
            
            await update.message.reply_text(f"🗑️ <b>Deleted {deleted} messages!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"🗑️ <b>Purged</b> {deleted} messages by {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ RELOAD COMMAND ─═◈═────
    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can reload!")
            return
        
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            await db.update_settings(chat.id, "admins", [admin.user.id for admin in admins])
            await update.message.reply_text(f"✅ <b>Admins list reloaded!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ STAFF COMMAND ─═◈═────
    async def staff_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
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
👥 <b>Staff List</b> 👥

────═◈═─ ✧◈✧ ─═◈═────
👑 <b>Owner:</b>
╰┈➤ {owner.first_name}

👔 <b>Admins: ({len(admin_list)})</b>
"""
            for admin in admin_list:
                staff_text += f"╰┈➤ {admin.first_name}\n"
            
            staff_text += f"\n📊 <b>Total Staff:</b> {len(admin_list) + 1}"
            staff_text += self.get_owner_credit()
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            await update.message.reply_text(staff_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ SETTINGS COMMAND ─═◈═────
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can view settings!")
            return
        
        settings = await db.get_settings(chat.id)
        
        keyboard = [
            [InlineKeyboardButton("🛡️ Anti-Spam", callback_data="set_antispam"), InlineKeyboardButton("🔗 Anti-Link", callback_data="set_antilink")],
            [InlineKeyboardButton("👋 Welcome", callback_data="set_welcome"), InlineKeyboardButton("👋 Goodbye", callback_data="set_goodbye")],
            [InlineKeyboardButton("🔞 Anti-18+", callback_data="set_anti18")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        settings_text = f"""
⚙️ <b>Settings Menu</b>

📍 <b>Group:</b> {chat.title}

<b>Current Settings:</b>
├ Anti-Spam: {'✅' if settings.get('antispam', True) else '❌'}
├ Anti-Link: {'✅' if settings.get('antilink', False) else '❌'}
├ Anti-18+: {'✅' if settings.get('anti18', True) else '❌'}
├ Welcome: {'✅' if settings.get('welcome', True) else '❌'}
├ Goodbye: {'✅' if settings.get('goodbye', True) else '❌'}
└ Warn Limit: {settings.get('warn_limit', 3)}

Select a setting to change.
{self.get_owner_credit()}
"""
        await update.message.reply_text(settings_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ RULES COMMANDS ─═◈═────
    async def set_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can set rules!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Please provide rules!\nExample: `/setrules No spam, No abuse`")
            return
        
        rules = " ".join(context.args)
        await db.set_rules(chat.id, rules)
        await update.message.reply_text(f"✅ <b>Rules set successfully!</b>\n\n📋 {rules}{self.get_owner_credit()}", parse_mode="HTML")

    async def get_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat = update.effective_chat
        rules = await db.get_rules(chat.id)
        
        if rules:
            await update.message.reply_text(f"📋 <b>Group Rules:</b>\n\n{rules}{self.get_owner_credit()}", parse_mode="HTML")
        else:
            await update.message.reply_text(f"ℹ️ No rules set for this group.\nAdmins can set rules using `/setrules`{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ PING COMMAND ─═◈═────
    async def ping_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            cpu_usage = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            ram_used = ram.used / (1024 ** 3)
            ram_total = ram.total / (1024 ** 3)
            ram_percent = ram.percent
            disk = psutil.disk_usage('/')
            disk_used = disk.used / (1024 ** 3)
            disk_total = disk.total / (1024 ** 3)
            disk_percent = disk.percent
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
        
        # Bot uptime
        bot_uptime = datetime.now() - self.start_time
        bot_uptime_str = str(bot_uptime).split('.')[0]
        
        start_time = datetime.now()
        msg = await update.message.reply_text("🏓 Pinging...")
        end_time = datetime.now()
        latency = (end_time - start_time).microseconds / 1000
        
        ping_text = f"""
⚡️ <b>{Config.BOT_NAME}</b>

🏓 Ping..Pong : <code>{latency:.3f}ms</code>

» <b>Bot Stats:</b>
:⧽ Uptime : <code>{bot_uptime_str}</code>
:⧽ Users : <code>{db.users.count_documents({})}</code>
:⧽ Groups : <code>{db.groups.count_documents({})}</code>

» <b>System Stats:</b>
:⧽ Uptime : <code>{uptime_str}</code>
:⧽ RAM : <code>{ram_used:.2f}GB / {ram_total:.2f}GB</code> ({ram_percent}%)
:⧽ CPU : <code>{cpu_usage}%</code>
:⧽ Disk : <code>{disk_used:.2f}GB / {disk_total:.2f}GB</code> ({disk_percent}%)

{self.get_owner_credit()}
"""
        
        await msg.edit_text(ping_text, parse_mode="HTML")

    # ────═◈═─ ABOUT COMMAND ─═◈═────
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        about_text = f"""
⚡ <b>About {Config.BOT_NAME}</b> ⚡

────═◈═─ ✧◈✧ ─═◈═────
🤖 <b>Name:</b> {Config.BOT_NAME}  
📌 <b>ID:</b> {Config.BOT_USERNAME} 
👑 <b>Owner:</b> {Config.OWNER_NAME} 
📞 <b>Contact:</b> {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 <b>Description:</b>
The Ultimate Group Protection Bot

⚙️ <b>Features:</b>
╰┈➤ Anti-Spam
╰┈➤ Anti-Link
╰┈➤ Anti-18+
╰┈➤ Warn System
╰┈➤ Mute/Unmute
╰┈➤ Ban/Kick
╰┈➤ Pin/Unpin
╰┈➤ Delete/Purge
╰┈➤ Filters
╰┈➤ SG (User History)
╰┈➤ History Tracking
╰┈➤ Smart Chat

📢 <b>Version:</b> 3.0.0
🔰 <b>Status:</b> Active

{self.get_owner_credit()}
"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await update.message.reply_text(about_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ PREMIUM COMMAND ─═◈═────
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        is_premium = user.id in Config.PREMIUM_USERS or user.id == Config.OWNER_ID
        
        if is_premium:
            text = f"""
💎 <b>Premium Status</b> 💎

✅ <b>You are a Premium User!</b>

<b>Unlocked Features:</b>
╰┈➤ Anti-Crash
╰┈➤ Advanced Anti-Spam
╰┈➤ Custom Welcome GIF
╰┈➤ Private Logs
╰┈➤ 24/7 Support
╰┈➤ Advanced Analytics
╰┈➤ Custom Commands

{self.get_owner_credit()}
"""
        else:
            text = f"""
💎 <b>Premium Plan</b> 💎

<b>Unlock Premium Features:</b>
╰┈➤ Anti-Crash
╰┈➤ Advanced Anti-Spam
╰┈➤ Custom Welcome GIF
╰┈➤ Private Logs
╰┈➤ 24/7 Support
╰┈➤ Advanced Analytics
╰┈➤ Custom Commands

<b>Price:</b> $5/month

Contact Owner to Buy:
📞 {Config.OWNER_USERNAME}

{self.get_owner_credit()}
"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ STATS COMMAND ─═◈═────
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != Config.OWNER_ID:
            await update.message.reply_text(f"❌ Only owner can view stats!{self.get_owner_credit()}", parse_mode="HTML")
            return
        
        users_count = db.users.count_documents({})
        groups_count = db.groups.count_documents({})
        warnings_count = db.warnings.count_documents({})
        mutes_count = db.mutes.count_documents({})
        premium_count = db.premium.count_documents({})
        history_count = db.user_history.count_documents({})
        filters_count = db.filters.count_documents({})
        
        stats_text = f"""
📊 <b>Bot Statistics</b> 📊

────═◈═─ ✧◈✧ ─═◈═────
👥 Total Users: {users_count}  
📍 Total Groups: {groups_count} 
⚠️ Warnings: {warnings_count}   
🔇 Active Mutes: {mutes_count} 
💎 Premium Users: {premium_count}
🔄 History Records: {history_count}
📋 Filters: {filters_count}
────═◈═─ ✧◈✧ ─═◈═────
🔥 <b>Bot Info:</b>
╰┈➤ Name: {Config.BOT_NAME}
╰┈➤ Version: 3.0.0
╰┈➤ Owner: {Config.OWNER_NAME}
⚡ <b>Status:</b> Online

{self.get_owner_credit()}
"""
        await update.message.reply_text(stats_text, parse_mode="HTML")

    # ────═◈═─ WELCOME CONTROL COMMANDS ─═◈═────
    async def enable_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can enable welcome!")
            return
        
        await db.update_settings(chat.id, "welcome", True)
        await update.message.reply_text(f"✅ <b>Welcome messages enabled for this group!</b>{self.get_owner_credit()}", parse_mode="HTML")

    async def disable_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can disable welcome!")
            return
        
        await db.update_settings(chat.id, "welcome", False)
        await update.message.reply_text(f"❌ <b>Welcome messages disabled for this group!</b>{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ MODERATION COMMANDS ─═◈═────
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can warn!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please provide a username or reply to a message!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        
        if target.is_bot:
            await update.message.reply_text("❌ Can't warn bots!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        await db.add_warning(target.id, chat.id, reason, user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        warn_count = len(warnings)
        max_warns = Config.MAX_WARNINGS
        
        warn_msg = f"""
⚠️ <b>Warning!</b> ⚠️

────═◈═─ ✧◈✧ ─═◈═────
👤 {target.first_name}
📊 Warn: {warn_count}/{max_warns}
📝 Reason: {reason}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
        await update.message.reply_text(warn_msg, parse_mode="HTML")
        
        await self.log_action(chat.id, f"⚠️ <b>Warn</b> {target.first_name} ({warn_count}/{max_warns}) by {user.first_name} - {reason}")
        
        if warn_count >= max_warns:
            mute_duration = Config.MUTE_DURATION
            await db.add_mute(target.id, chat.id, mute_duration, "Exceeded warn limit", user.id)
            try:
                await context.bot.restrict_chat_member(
                    chat.id,
                    target.id,
                    ChatPermissions(can_send_messages=False)
                )
                mute_msg = f"""
🔇 <b>Auto-Muted!</b> 🔇

────═◈═─ ✧◈✧ ─═◈═────
👤 {target.first_name}
⏱️ {mute_duration}s
📝 Reason: Exceeded warn limit
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
                await update.message.reply_text(mute_msg, parse_mode="HTML")
            except:
                pass

    async def unwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can remove warns!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        target = None
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        
        warnings = await db.get_warnings(target.id, chat.id)
        if warnings:
            await db.clear_warnings(target.id, chat.id)
            await update.message.reply_text(f"✅ <b>Removed all warns for {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"✅ <b>Unwarn</b> {target.first_name} by {user.first_name}")
        else:
            await update.message.reply_text(f"ℹ️ {target.first_name} has no warns!{self.get_owner_credit()}", parse_mode="HTML")

    async def warns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        chat = update.effective_chat
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            target = update.effective_user
        
        warnings = await db.get_warnings(target.id, chat.id)
        
        if not warnings:
            await update.message.reply_text(f"✅ {target.first_name} has no warnings!{self.get_owner_credit()}", parse_mode="HTML")
            return
        
        warn_text = f"⚠️ <b>Warnings for {target.first_name}:</b>\n\n"
        for i, warn in enumerate(warnings, 1):
            warn_text += f"└ {i}. {warn['reason']}\n"
        warn_text += self.get_owner_credit()
        
        await update.message.reply_text(warn_text, parse_mode="HTML")

    async def delwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can use this command!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Please reply to a message!")
            return
        
        target = update.message.reply_to_message.from_user
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await context.bot.delete_message(chat.id, update.message.message_id)
        await db.add_warning(target.id, chat.id, "Deleted message", user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        
        await update.message.reply_text(f"⚠️ <b>Deleted message & warned {target.first_name}!</b> ({len(warnings)}/{Config.MAX_WARNINGS}){self.get_owner_credit()}", parse_mode="HTML")

    async def reset_warns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can reset warns!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        await db.clear_warnings(target.id, chat.id)
        await update.message.reply_text(f"✅ <b>Reset all warns for {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ MUTE/UNMUTE COMMANDS ─═◈═────
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can mute!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ Can't mute bots!")
            return
        
        duration = Config.MUTE_DURATION
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        try:
            if len(context.args) > 1 and context.args[1].isdigit():
                duration = int(context.args[1])
                reason = " ".join(context.args[2:]) if len(context.args) > 2 else "No reason provided"
            
            await db.add_mute(target.id, chat.id, duration, reason, user.id)
            await context.bot.restrict_chat_member(
                chat.id,
                target.id,
                ChatPermissions(can_send_messages=False)
            )
            
            mute_msg = f"""
🔇 <b>Muted!</b> 🔇

────═◈═─ ✧◈✧ ─═◈═────
👤 {target.first_name}
⏱️ {duration}s
📝 Reason: {reason}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
            await update.message.reply_text(mute_msg, parse_mode="HTML")
            await self.log_action(chat.id, f"🔇 <b>Mute</b> {target.first_name} ({duration}s) by {user.first_name} - {reason}")
            
            asyncio.create_task(self.auto_unmute(context, chat.id, target.id, duration))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

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
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can unmute!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
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
            await update.message.reply_text(f"🔊 <b>Unmuted {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"🔊 <b>Unmute</b> {target.first_name} by {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ KICK/BAN/UNBAN COMMANDS ─═◈═────
    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can kick!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ Can't kick bots!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"👢 <b>Kicked {target.first_name}!</b>\n📝 Reason: {reason}{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"👢 <b>Kick</b> {target.first_name} by {user.first_name} - {reason}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can ban!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ Can't ban bots!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason provided"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"🚫 <b>Banned {target.first_name}!</b>\n📝 Reason: {reason}{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"🚫 <b>Ban</b> {target.first_name} by {user.first_name} - {reason}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can unban!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        else:
            await update.message.reply_text("⚠️ Please provide a username!")
            return
        
        try:
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"✅ <b>Unbanned {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"✅ <b>Unban</b> {target.first_name} by {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ APPROVE/UNAPPROVE COMMANDS ─═◈═────
    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can approve!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        await db.approve_user(target.id, chat.id)
        await update.message.reply_text(f"✅ <b>Approved</b> {target.first_name}!\n🔗 Now You Are Free.{self.get_owner_credit()}", parse_mode="HTML")
        await self.log_action(chat.id, f"✅ <b>Approve</b> {target.first_name} by {user.first_name}")

    async def unapprove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ This command only works in groups!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Only admins can unapprove!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ User not found!")
                return
        elif update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
        else:
            await update.message.reply_text("⚠️ Please provide a user!")
            return
        
        await db.unapprove_user(target.id, chat.id)
        await update.message.reply_text(f"❌ <b>Unapproved</b> {target.first_name}!\n🔗 No more links.{self.get_owner_credit()}", parse_mode="HTML")
        await self.log_action(chat.id, f"❌ <b>Unapprove</b> {target.first_name} by {user.first_name}")

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
                    await db.add_warning(user.id, chat.id, "Spamming", "Bot")
                    await update.message.reply_text(f"⚠️ {user.first_name} warned for spam! ({warn_count+1}/{Config.MAX_WARNINGS})")

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
                f"🔗 <b>Link Detected!</b>\n\n{user.first_name}, you are not approved to send links.\nContact an admin to get approval.{self.get_owner_credit()}",
                parse_mode="HTML"
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
        
        adult_keywords = ['porn', 'xxx', 'sex', 'nude', 'nsfw', '18+', 'adult', 'fuck', 'shit', 'bitch', 'ass']
        if any(keyword in update.message.text.lower() for keyword in adult_keywords):
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(
                f"🔞 <b>18+ Content Detected!</b>\n\n{user.first_name}, this type of content is not allowed.{self.get_owner_credit()}",
                parse_mode="HTML"
            )

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
                [InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"), InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")],
                [InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"), InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")],
                [InlineKeyboardButton("👥 sᴛᴀғғ", callback_data="staff"), InlineKeyboardButton("🔄 SG", callback_data="sg")],
                [InlineKeyboardButton("📜 ʜɪsᴛᴏʀʏ", callback_data="history"), InlineKeyboardButton("💬 ᴄʜᴀᴛ", callback_data="chat")]
            ]
            if is_premium:
                keyboard.append([InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")])
            
            try:
                await query.edit_message_text(
                    main_text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    main_text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif data == "sg":
            await query.edit_message_text(
                f"🔄 <b>SG - User History Tracking</b>\n\n"
                f"Use /sg @username or reply to a user's message\n"
                f"To view their complete history!\n\n"
                f"📊 <b>Features:</b>\n"
                f"├ Name Changes\n"
                f"├ Username Changes\n"
                f"├ Message Count\n"
                f"└ Groups Joined{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "history":
            await query.edit_message_text(
                f"📜 <b>History Tracking</b>\n\n"
                f"Use /history @username or reply to a user's message\n"
                f"To view their complete change history!\n\n"
                f"📊 <b>Tracks:</b>\n"
                f"├ Every Name Change\n"
                f"├ Every Username Change\n"
                f"├ Timestamp of Changes\n"
                f"└ Total Changes{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "chat":
            await query.edit_message_text(
                f"💬 <b>Chat with me!</b>\n\n"
                f"Send me any message and I'll respond!\n"
                f"Try asking me about:\n"
                f"• Your info\n"
                f"• Group stats\n"
                f"• Commands\n"
                f"• Anything else!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
        
        elif data == "staff":
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            try:
                await query.edit_message_text(
                    f"👥 Use /staff to view staff list{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"👥 Use /staff to view staff list{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif data == "about":
            text = f"""
⚡ <b>About {Config.BOT_NAME}</b> ⚡

────═◈═─ ✧◈✧ ─═◈═────
🤖 <b>Name:</b> {Config.BOT_NAME}  
📌 <b>ID:</b> {Config.BOT_USERNAME} 
👑 <b>Owner:</b> {Config.OWNER_NAME} 
📞 <b>Contact:</b> {Config.OWNER_USERNAME} 
────═◈═─ ✧◈✧ ─═◈═────

💫 <b>Description:</b>
The Ultimate Group Protection Bot

⚙️ <b>Features:</b>
╰┈➤ Anti-Spam
╰┈➤ Anti-Link
╰┈➤ Anti-18+
╰┈➤ Warn System
╰┈➤ Mute/Unmute
╰┈➤ Ban/Kick
╰┈➤ Pin/Unpin
╰┈➤ Delete/Purge
╰┈➤ Filters
╰┈➤ SG (User History)
╰┈➤ History Tracking
╰┈➤ Smart Chat

📢 <b>Version:</b> 3.0.0
🔰 <b>Status:</b> Active

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "help":
            text = f"""
📖 <b>Commands List</b> 📖

<b>👑 Admin Commands:</b>
╰┈➤ /warn @user - Warn user
╰┈➤ /unwarn @user - Remove warn
╰┈➤ /warns @user - Check warns
╰┈➤ /mute @user - Mute user
╰┈➤ /unmute @user - Unmute user
╰┈➤ /kick @user - Kick user
╰┈➤ /ban @user - Ban user
╰┈➤ /unban @user - Unban user
╰┈➤ /pin - Pin message
╰┈➤ /unpin - Unpin
╰┈➤ /del - Delete
╰┈➤ /purge - Purge messages
╰┈➤ /settings - Manage settings
╰┈➤ /setrules - Set rules
╰┈➤ /rules - View rules
╰┈➤ /approve @user - Approve user
╰┈➤ /filter keyword reply - Add filter
╰┈➤ /stopfilter keyword - Remove filter
╰┈➤ /filters - List filters

<b>📊 General Commands:</b>
╰┈➤ /start - Start bot
╰┈➤ /help - Get help
╰┈➤ /about - About bot
╰┈➤ /ping - Check bot
╰┈➤ /staff - View staff
╰┈➤ /info @user - User info
╰┈➤ /me - Your info
╰┈➤ /sg @user - User history
╰┈➤ /history @user - Full history
╰┈➤ /chat - Chat with bot

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "stats":
            if user_id != Config.OWNER_ID:
                try:
                    await query.edit_message_text(f"❌ Only owner can view stats!{self.get_owner_credit()}", parse_mode="HTML")
                except:
                    await query.message.reply_text(f"❌ Only owner can view stats!{self.get_owner_credit()}", parse_mode="HTML")
                return
            
            users_count = db.users.count_documents({})
            groups_count = db.groups.count_documents({})
            warnings_count = db.warnings.count_documents({})
            mutes_count = db.mutes.count_documents({})
            premium_count = db.premium.count_documents({})
            history_count = db.user_history.count_documents({})
            
            text = f"""
📊 <b>Bot Statistics</b> 📊

────═◈═─ ✧◈✧ ─═◈═────
👥 Total Users: {users_count}  
📍 Total Groups: {groups_count} 
⚠️ Warnings: {warnings_count}   
🔇 Active Mutes: {mutes_count} 
💎 Premium Users: {premium_count}
🔄 History Records: {history_count}
────═◈═─ ✧◈✧ ─═◈═────
🔥 <b>Bot Info:</b>
╰┈➤ Name: {Config.BOT_NAME}
╰┈➤ Version: 3.0.0
╰┈➤ Owner: {Config.OWNER_NAME}
⚡ <b>Status:</b> Online

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("👋 Welcome", callback_data="set_welcome"), InlineKeyboardButton("👋 Goodbye", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ Anti-Spam", callback_data="set_antispam"), InlineKeyboardButton("🔗 Anti-Link", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 Anti-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(
                    f"⚙️ <b>Settings Menu</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"⚙️ <b>Settings Menu</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        
        elif data == "premium":
            if is_premium:
                text = f"""
💎 <b>Premium Status</b> 💎
✅ <b>You are a Premium User!</b>

<b>Unlocked Features:</b>
╰┈➤ Anti-Crash
╰┈➤ Advanced Anti-Spam
╰┈➤ Custom Welcome GIF
╰┈➤ Private Logs
╰┈➤ 24/7 Support
╰┈➤ Advanced Analytics
╰┈➤ Custom Commands

{self.get_owner_credit()}
"""
            else:
                text = f"""
💎 <b>Premium Plan</b> 💎

<b>Unlock Premium Features:</b>
╰┈➤ Anti-Crash
╰┈➤ Advanced Anti-Spam
╰┈➤ Custom Welcome GIF
╰┈➤ Private Logs
╰┈➤ 24/7 Support
╰┈➤ Advanced Analytics
╰┈➤ Custom Commands

<b>Price:</b> $5/month

Contact Owner to Buy:
📞 {Config.OWNER_USERNAME}

{self.get_owner_credit()}
"""
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            try:
                await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif data.startswith("toggle_"):
            setting = data.replace("toggle_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            try:
                await query.edit_message_text(f"✅ <b>{setting.upper()}</b> {'Enabled' if not current else 'Disabled'}!{self.get_owner_credit()}", parse_mode="HTML")
            except:
                await query.message.reply_text(f"✅ <b>{setting.upper()}</b> {'Enabled' if not current else 'Disabled'}!{self.get_owner_credit()}", parse_mode="HTML")
            
            await asyncio.sleep(1)
            
            keyboard = [
                [InlineKeyboardButton("👋 Welcome", callback_data="set_welcome"), InlineKeyboardButton("👋 Goodbye", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ Anti-Spam", callback_data="set_antispam"), InlineKeyboardButton("🔗 Anti-Link", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 Anti-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ]
            try:
                await query.edit_message_text(
                    f"⚙️ <b>Settings Menu</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"⚙️ <b>Settings Menu</b>\n\n{self.get_owner_credit()}",
                    parse_mode="HTML",
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
                [InlineKeyboardButton(f"{'✅' if current else '❌'} Toggle", callback_data=f"toggle_{setting}")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings")]
            ]
            display_name = data.replace("set_", "").upper()
            try:
                await query.edit_message_text(
                    f"{display_name}\n\nCurrent Status: {'✅ Enabled' if current else '❌ Disabled'}{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                await query.message.reply_text(
                    f"{display_name}\n\nCurrent Status: {'✅ Enabled' if current else '❌ Disabled'}{self.get_owner_credit()}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

    # ────═◈═─ ERROR HANDLER ─═◈═────
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}")
        try:
            if update and update.effective_chat:
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"❌ <b>An error occurred!</b>\n"
                    f"Error: <code>{str(context.error)[:100]}</code>{self.get_owner_credit()}",
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
            
            # Welcome control commands
            self.app.add_handler(CommandHandler("enablewelcome", self.enable_welcome))
            self.app.add_handler(CommandHandler("disablewelcome", self.disable_welcome))
            
            # SG and History commands
            self.app.add_handler(CommandHandler("sg", self.sg_command))
            self.app.add_handler(CommandHandler("history", self.history_command))
            self.app.add_handler(CommandHandler("chat", self.chat_command))
            
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
            premium_print(f"ʟᴏɢ ᴄʜᴀɴɴᴇʟ: {self.log_channel}", "📝")
            
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
