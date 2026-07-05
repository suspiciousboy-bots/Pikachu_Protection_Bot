#!/usr/bin/env python3
"""
⚡ PIKACHU X PROTECTION BOT - ULTIMATE GROUP MANAGEMENT ⚡
"""

import os
import sys
import asyncio
import logging
import re
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

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

    async def is_mod(self, context, chat_id, user_id):
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except:
            return False

    async def get_user_role(self, user_id, chat_id):
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
        try:
            bot_member = await self.app.bot.get_chat_member(chat_id, self.app.bot.id)
            if bot_member.status in ['administrator', 'creator', 'member']:
                return True
        except:
            pass
        return False

    async def bot_added_checker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        welcome_text = f"""
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
║  <b>WELCOME TO THE PARTY!</b>     ║
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
💔 <b>Gᴏᴏᴅʙʏᴇ!</b> 💔

<b>Nᴀᴍᴇ:</b> {member.first_name}
📍 <b>Gʀᴏᴜᴘ:</b> {chat.title}

😢 Wᴇ ᴡɪʟʟ ᴍɪss ʏᴏᴜ!
{self.get_owner_credit()}
"""
        await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode="HTML"
        )

    # ────═◈═─ PREMIUM COMMAND ─═◈═────
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        bot_uptime = datetime.now() - self.start_time
        bot_uptime_str = str(bot_uptime).split('.')[0]
        
        start_time = datetime.now()
        msg = await update.message.reply_text("🏓 Pɪɴɢɪɴɢ...")
        end_time = datetime.now()
        latency = (end_time - start_time).microseconds / 1000
        
        ping_text = f"""
⚡️ <b>{Config.BOT_NAME}</b>

🏓 Pɪɴɢ..Pᴏɴɢ : <code>{latency:.3f}ms</code>

» <b>Bᴏᴛ Sᴛᴀᴛs:</b>
:⧽ Uᴘᴛɪᴍᴇ : <code>{bot_uptime_str}</code>
:⧽ Uꜱᴇʀs : <code>{db.users.count_documents({})}</code>
:⧽ Gʀᴏᴜᴘs : <code>{db.groups.count_documents({})}</code>

» <b>Sʏsᴛᴇᴍ Sᴛᴀᴛs:</b>
:⧽ Uᴘᴛɪᴍᴇ : <code>{uptime_str}</code>
:⧽ Rᴀᴍ : <code>{ram_used:.2f}GB / {ram_total:.2f}GB</code> ({ram_percent}%)
:⧽ Cᴘᴜ : <code>{cpu_usage}%</code>
:⧽ Dɪsᴋ : <code>{disk_used:.2f}GB / {disk_total:.2f}GB</code> ({disk_percent}%)

{self.get_owner_credit()}
"""
        
        await msg.edit_text(ping_text, parse_mode="HTML")

    # ────═◈═─ STATS COMMAND ─═◈═────
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != Config.OWNER_ID:
            await update.message.reply_text(f"❌ Oɴʟʏ ᴏᴡɴᴇʀ ᴄᴀɴ ᴠɪᴇᴡ sᴛᴀᴛs!{self.get_owner_credit()}", parse_mode="HTML")
            return
        
        users_count = db.users.count_documents({})
        groups_count = db.groups.count_documents({})
        warnings_count = db.warnings.count_documents({})
        mutes_count = db.mutes.count_documents({})
        premium_count = db.premium.count_documents({})
        history_count = db.user_history.count_documents({})
        filters_count = db.filters.count_documents({})
        
        stats_text = f"""
📊 <b>Bᴏᴛ Sᴛᴀᴛɪsᴛɪᴄs</b> 📊

────═◈═─ ✧◈✧ ─═◈═────
👥 Tᴏᴛᴀʟ Uꜱᴇʀs: {users_count}  
📍 Tᴏᴛᴀʟ Gʀᴏᴜᴘs: {groups_count} 
⚠️ Wᴀʀɴɪɴɢs: {warnings_count}   
🔇 Aᴄᴛɪᴠᴇ Mᴜᴛᴇs: {mutes_count} 
💎 Pʀᴇᴍɪᴜᴍ Uꜱᴇʀs: {premium_count}
🔄 Hɪsᴛᴏʀʏ Rᴇᴄᴏʀᴅs: {history_count}
📋 Fɪʟᴛᴇʀs: {filters_count}
────═◈═─ ✧◈✧ ─═◈═────
🔥 <b>Bᴏᴛ Iɴғᴏ:</b>
╰┈➤ Nᴀᴍᴇ: {Config.BOT_NAME}
╰┈➤ Vᴇʀsɪᴏɴ: 3.0.0
╰┈➤ Oᴡɴᴇʀ: {Config.OWNER_NAME}
⚡ <b>Sᴛᴀᴛᴜs:</b> Oɴʟɪɴᴇ

{self.get_owner_credit()}
"""
        await update.message.reply_text(stats_text, parse_mode="HTML")

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
╰┈➤ /reload - Rᴇʟᴏᴀᴅ ᴀᴅᴍɪɴs
╰┈➤ /settings - Mᴀɴᴀɢᴇ sᴇᴛᴛɪɴɢs
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

    # ────═◈═─ INFOPVT COMMAND ─═◈═────
    async def infopvt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            user_full = await context.bot.get_chat(target.id)
            bio = getattr(user_full, 'bio', 'Nᴏ ʙɪᴏ sᴇᴛ')
            history_count = len(await db.get_user_history(target.id))
            msg_count = await db.get_user_message_count(target.id)
            
            info_text = f"""
📋 <b>Uꜱᴇʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Nᴀᴍᴇ:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{target.username if target.username else 'Nᴏɴᴇ'}
📝 <b>Bɪᴏ:</b> {bio[:100] if bio != 'Nᴏ ʙɪᴏ sᴇᴛ' else 'Nᴏ ʙɪᴏ sᴇᴛ'}
📊 <b>Mᴇssᴀɢᴇs:</b> {msg_count}
🔄 <b>Nᴀᴍᴇ Cʜᴀɴɢᴇs:</b> {history_count}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
            await context.bot.send_message(update.effective_user.id, info_text, parse_mode="HTML")
            await update.message.reply_text(f"✅ <b>Iɴғᴏʀᴍᴀᴛɪᴏɴ sᴇɴᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ!</b>{self.get_owner_credit()}", parse_mode="HTML")
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
📋 <b>Yᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Nᴀᴍᴇ:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else 'Nᴏɴᴇ'}
⚠️ <b>Wᴀʀɴɪɴɢs:</b> {len(warnings)}
📊 <b>Mᴇssᴀɢᴇs:</b> {msg_count}
🔄 <b>Nᴀᴍᴇ Cʜᴀɴɢᴇs:</b> {history_count}
📋 <b>Rᴜʟᴇs:</b> {rules[:100] if rules else 'Nᴏ ʀᴜʟᴇs sᴇᴛ'}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
        await update.message.reply_text(me_text, parse_mode="HTML")

    # ────═◈═─ GETURL COMMAND ─═◈═────
    async def geturl_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ɢᴇᴛ ɪᴛs ʟɪɴᴋ!")
            return
        
        chat = update.effective_chat
        msg = update.message.reply_to_message
        link = f"https://t.me/{chat.username}/{msg.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{msg.message_id}"
        await update.message.reply_text(f"🔗 <b>Mᴇssᴀɢᴇ Lɪɴᴋ:</b>\n{link}{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ PINNED COMMAND ─═◈═────
    async def pinned_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat = update.effective_chat
        try:
            pinned = await context.bot.get_chat(chat.id)
            if pinned.pinned_message:
                link = f"https://t.me/{chat.username}/{pinned.pinned_message.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{pinned.pinned_message.message_id}"
                await update.message.reply_text(f"📌 <b>Cᴜʀʀᴇɴᴛ Pɪɴɴᴇᴅ Mᴇssᴀɢᴇ:</b>\n{link}{self.get_owner_credit()}", parse_mode="HTML")
            else:
                await update.message.reply_text(f"📌 <b>Nᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except:
            await update.message.reply_text(f"❌ Uɴᴀʙʟᴇ ᴛᴏ ғᴇᴛᴄʜ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!{self.get_owner_credit()}", parse_mode="HTML")

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

    # ────═◈═─ SETTINGS COMMAND ─═◈═────
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴠɪᴇᴡ sᴇᴛᴛɪɴɢs!")
            return
        
        settings = await db.get_settings(chat.id)
        
        keyboard = [
            [InlineKeyboardButton("🛡️ Aɴᴛɪ-Sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 Aɴᴛɪ-Lɪɴᴋ", callback_data="set_antilink")],
            [InlineKeyboardButton("👋 Wᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 Gᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
            [InlineKeyboardButton("🔞 Aɴᴛɪ-18+", callback_data="set_anti18")],
            [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
        ]
        
        settings_text = f"""
⚙️ <b>Sᴇᴛᴛɪɴɢs Mᴇɴᴜ</b>

📍 <b>Gʀᴏᴜᴘ:</b> {chat.title}

<b>Cᴜʀʀᴇɴᴛ Sᴇᴛᴛɪɴɢs:</b>
├ Aɴᴛɪ-Sᴘᴀᴍ: {'✅' if settings.get('antispam', True) else '❌'}
├ Aɴᴛɪ-Lɪɴᴋ: {'✅' if settings.get('antilink', False) else '❌'}
├ Aɴᴛɪ-18+: {'✅' if settings.get('anti18', True) else '❌'}
├ Wᴇʟᴄᴏᴍᴇ: {'✅' if settings.get('welcome', True) else '❌'}
├ Gᴏᴏᴅʙʏᴇ: {'✅' if settings.get('goodbye', True) else '❌'}
└ Wᴀʀɴ Lɪᴍɪᴛ: {settings.get('warn_limit', 3)}

Sᴇʟᴇᴄᴛ ᴀ sᴇᴛᴛɪɴɢ ᴛᴏ ᴄʜᴀɴɢᴇ.
{self.get_owner_credit()}
"""
        await update.message.reply_text(settings_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

    # ────═◈═─ RULES COMMANDS ─═◈═────
    async def set_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ʀᴜʟᴇs!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ʀᴜʟᴇs!\nExᴀᴍᴘʟᴇ: `/setrules Nᴏ sᴘᴀᴍ, Nᴏ ᴀʙᴜsᴇ`")
            return
        
        rules = " ".join(context.args)
        await db.set_rules(chat.id, rules)
        await update.message.reply_text(f"✅ <b>Rᴜʟᴇs sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>\n\n📋 {rules}{self.get_owner_credit()}", parse_mode="HTML")

    async def get_rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        rules = await db.get_rules(chat.id)
        
        if rules:
            await update.message.reply_text(f"📋 <b>Gʀᴏᴜᴘ Rᴜʟᴇs:</b>\n\n{rules}{self.get_owner_credit()}", parse_mode="HTML")
        else:
            await update.message.reply_text(f"ℹ️ Nᴏ ʀᴜʟᴇs sᴇᴛ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.\nAᴅᴍɪɴs ᴄᴀɴ sᴇᴛ ʀᴜʟᴇs ᴜsɪɴɢ `/setrules`{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ WELCOME CONTROL COMMANDS ─═◈═────
    async def enable_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ!")
            return
        
        await db.update_settings(chat.id, "welcome", True)
        await update.message.reply_text(f"✅ <b>Wᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!</b>{self.get_owner_credit()}", parse_mode="HTML")

    async def disable_welcome(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴅɪsᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ!")
            return
        
        await db.update_settings(chat.id, "welcome", False)
        await update.message.reply_text(f"❌ <b>Wᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!</b>{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ HISTORY COMMAND ─═◈═────
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        if not history:
            await update.message.reply_text(f"📜 Nᴏ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ ғᴏʀ {target.first_name}!", parse_mode="HTML")
            return
        
        if len(history) > 50:
            history_text = f"Uꜱᴇʀ Hɪsᴛᴏʀʏ Fᴏʀ {target.first_name} (ID: {target.id})\n"
            history_text += "=" * 50 + "\n\n"
            
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', 'Unknown')
                name = entry.get('first_name', 'Unknown')
                username = entry.get('username', 'None')
                history_text += f"{i}. {timestamp}\n   Nᴀᴍᴇ: {name}\n   Uꜱᴇʀɴᴀᴍᴇ: @{username}\n\n"
            
            history_text += self.get_owner_credit()
            
            with open(f"history_{target.id}.txt", "w", encoding="utf-8") as f:
                f.write(history_text)
            
            with open(f"history_{target.id}.txt", "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"history_{target.id}.txt",
                    caption=f"📜 Fᴜʟʟ ʜɪsᴛᴏʀʏ ғᴏʀ {target.first_name}"
                )
            
            os.remove(f"history_{target.id}.txt")
        else:
            msg = f"📜 <b>Hɪsᴛᴏʀʏ Fᴏʀ {target.first_name}</b>\n\n"
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
        await update.message.reply_text(
            f"💬 <b>Cʜᴀᴛ ᴡɪᴛʜ ᴍᴇ!</b>\n\n"
            f"Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴀɴᴅ I'ʟʟ ʀᴇsᴘᴏɴᴅ!\n"
            f"Tʀʏ ᴀsᴋɪɴɢ ᴍᴇ ᴀʙᴏᴜᴛ:\n"
            f"• Yᴏᴜʀ ɪɴғᴏ\n"
            f"• Gʀᴏᴜᴘ sᴛᴀᴛs\n"
            f"• Cᴏᴍᴍᴀɴᴅs\n"
            f"• Aɴʏᴛʜɪɴɢ ᴇʟsᴇ!{self.get_owner_credit()}",
            parse_mode="HTML"
        )

    # ────═◈═─ SMART CHAT HANDLER ─═◈═────
    async def smart_chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        text = update.message.text.lower()
        
        await db.increment_user_messages(user.id, chat.id)
        
        responses = {
            'hi': f"👋 Hᴇʟʟᴏ {user.first_name}! Hᴏᴡ ᴄᴀɴ I ʜᴇʟᴘ ʏᴏᴜ?",
            'hello': f"👋 Hɪ {user.first_name}! Nɪᴄᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ!",
            'hey': f"👋 Hᴇʏ {user.first_name}! Wʜᴀᴛ's ᴜᴘ?",
            'how are you': f"🤖 I'ᴍ ɢʀᴇᴀᴛ! Tʜᴀɴᴋs ғᴏʀ ᴀsᴋɪɴɢ, {user.first_name}!",
            'who are you': f"🤖 I'ᴍ Pɪᴋᴀᴄʜᴜ Pʀᴏᴛᴇᴄᴛɪᴏɴ Bᴏᴛ, ᴛʜᴇ ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ!",
            'what is your name': f"🤖 Mʏ ɴᴀᴍᴇ ɪs {Config.BOT_NAME}!",
            'thank you': f"🙌 Yᴏᴜ'ʀᴇ ᴡᴇʟᴄᴏᴍᴇ, {user.first_name}!",
            'thanks': f"🙌 Nᴏ ᴘʀᴏʙʟᴇᴍ, {user.first_name}!",
            'goodbye': f"👋 Gᴏᴏᴅʙʏᴇ, {user.first_name}! Sᴇᴇ ʏᴏᴜ ʟᴀᴛᴇʀ!",
            'bye': f"👋 Bʏᴇ {user.first_name}! Hᴀᴠᴇ ᴀ ɢʀᴇᴀᴛ ᴅᴀʏ!",
            'help': f"📖 Uꜱᴇ /ʜᴇʟᴘ ᴛᴏ sᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs!",
            'info': f"📊 Uꜱᴇ /ɪɴғᴏ ᴛᴏ ɢᴇᴛ ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ!",
            'ping': f"🏓 Uꜱᴇ /ᴘɪɴɢ ᴛᴏ ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛᴜs!",
            'love you': f"❤️ Lᴏᴠᴇ ʏᴏᴜ ᴛᴏᴏ, {user.first_name}!",
            'i love you': f"❤️ I ʟᴏᴠᴇ ʏᴏᴜ ᴛᴏᴏ, {user.first_name}!",
            'you are best': f"🌟 Tʜᴀɴᴋ ʏᴏᴜ, {user.first_name}! Yᴏᴜ'ʀᴇ ᴛʜᴇ ʙᴇsᴛ!",
        }
        
        for key, response in responses.items():
            if key in text:
                await update.message.reply_text(response + self.get_owner_credit(), parse_mode="HTML")
                return
        
        if 'my' in text and ('info' in text or 'id' in text or 'details' in text):
            info = f"""
📋 <b>Yᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

👤 <b>Nᴀᴍᴇ:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else 'Nᴏɴᴇ'}
📊 <b>Mᴇssᴀɢᴇs:</b> {await db.get_user_message_count(user.id)}
{self.get_owner_credit()}
"""
            await update.message.reply_text(info, parse_mode="HTML")
            return
        
        if 'group' in text and ('info' in text or 'stats' in text):
            try:
                member_count = await context.bot.get_chat_member_count(chat.id)
                admins = await context.bot.get_chat_administrators(chat.id)
                
                group_info = f"""
📊 <b>Gʀᴏᴜᴘ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

📍 <b>Nᴀᴍᴇ:</b> {chat.title}
👥 <b>Mᴇᴍʙᴇʀs:</b> {member_count}
👔 <b>Aᴅᴍɪɴs:</b> {len(admins)}
🆔 <b>ID:</b> <code>{chat.id}</code>
{self.get_owner_credit()}
"""
                await update.message.reply_text(group_info, parse_mode="HTML")
                return
            except:
                pass

    # ────═◈═─ FILTER COMMANDS ─═◈═────
    async def add_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴅᴅ ғɪʟᴛᴇʀs!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Uꜱᴀɢᴇ: `/filter ᴋᴇʏᴡᴏʀᴅ ʀᴇᴘʟʏ ᴛᴇxᴛ`\n\nExᴀᴍᴘʟᴇ: `/filter ʜᴇʟʟᴏ Hɪ ᴛʜᴇʀᴇ!`")
            return
        
        args = " ".join(context.args).split(" ", 1)
        if len(args) < 2:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀɴᴅ ʀᴇᴘʟʏ ᴛᴇxᴛ!")
            return
        
        keyword = args[0].lower()
        reply_text = args[1]
        
        await db.add_filter(chat.id, keyword, reply_text)
        await update.message.reply_text(f"✅ <b>Fɪʟᴛᴇʀ ᴀᴅᴅᴇᴅ!</b>\n\n📌 <b>Kᴇʏᴡᴏʀᴅ:</b> <code>{keyword}</code>\n📝 <b>Rᴇᴘʟʏ:</b> {reply_text}{self.get_owner_credit()}", parse_mode="HTML")

    async def remove_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ғɪʟᴛᴇʀs!")
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Uꜱᴀɢᴇ: `/stopfilter ᴋᴇʏᴡᴏʀᴅ`")
            return
        
        keyword = context.args[0].lower()
        await db.remove_filter(chat.id, keyword)
        await update.message.reply_text(f"✅ <b>Fɪʟᴛᴇʀ ʀᴇᴍᴏᴠᴇᴅ!</b>\n\n📌 <b>Kᴇʏᴡᴏʀᴅ:</b> <code>{keyword}</code>{self.get_owner_credit()}", parse_mode="HTML")

    async def list_filters(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        filters = await db.get_filters(chat.id)
        
        if not filters:
            await update.message.reply_text(f"ℹ️ <b>Nᴏ ғɪʟᴛᴇʀs sᴇᴛ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!</b>\n\nUꜱᴇ `/filter ᴋᴇʏᴡᴏʀᴅ ʀᴇᴘʟʏ` ᴛᴏ ᴀᴅᴅ ᴏɴᴇ.{self.get_owner_credit()}", parse_mode="HTML")
            return
        
        filter_text = "📋 <b>Aᴄᴛɪᴠᴇ Fɪʟᴛᴇʀs:</b>\n\n"
        for f in filters:
            filter_text += f"├ <b>{f['keyword']}</b> → {f['reply_text'][:50]}...\n"
        
        filter_text += f"\n📊 <b>Tᴏᴛᴀʟ:</b> {len(filters)} ғɪʟᴛᴇʀs"
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

    # ────═◈═─ PIN COMMANDS ─═◈═────
    async def pin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘɪɴ ᴍᴇssᴀɢᴇs!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ!")
            return
        
        try:
            await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
            await update.message.reply_text(f"📌 <b>Pɪɴɴᴇᴅ!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"📌 <b>Pɪɴɴᴇᴅ</b> ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def unpin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs!")
            return
        
        try:
            await context.bot.unpin_chat_message(chat.id)
            await update.message.reply_text(f"📌 <b>Uɴᴘɪɴɴᴇᴅ!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"📌 <b>Uɴᴘɪɴɴᴇᴅ</b> ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ DELETE/PURGE COMMANDS ─═◈═────
    async def del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ!")
            return
        
        try:
            await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await self.log_action(chat.id, f"🗑️ <b>Dᴇʟᴇᴛᴇᴅ</b> ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def logdel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        msg = update.message.reply_to_message
        try:
            log_msg = f"""
🗑️ <b>Lᴏɢ Dᴇʟᴇᴛᴇᴅ Mᴇssᴀɢᴇ</b>

📝 <b>Cᴏɴᴛᴇɴᴛ:</b> {msg.text if msg.text else 'Mᴇᴅɪᴀ'}
👤 <b>Uꜱᴇʀ:</b> {msg.from_user.first_name}
🆔 <b>ID:</b> <code>{msg.from_user.id}</code>
👮 <b>Bʏ:</b> {user.first_name}
📍 <b>Gʀᴏᴜᴘ:</b> {chat.title}
"""
            await self.log_action(chat.id, log_msg)
            await context.bot.delete_message(chat.id, msg.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(f"✅ <b>Dᴇʟᴇᴛᴇᴅ ᴀɴᴅ ʟᴏɢɢᴇᴅ!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def purge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘᴜʀɢᴇ ғʀᴏᴍ!")
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
            
            await update.message.reply_text(f"🗑️ <b>Dᴇʟᴇᴛᴇᴅ {deleted} ᴍᴇssᴀɢᴇs!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"🗑️ <b>Pᴜʀɢᴇᴅ</b> {deleted} ᴍᴇssᴀɢᴇs ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ RELOAD COMMAND ─═◈═────
    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇʟᴏᴀᴅ!")
            return
        
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            await db.update_settings(chat.id, "admins", [admin.user.id for admin in admins])
            await update.message.reply_text(f"✅ <b>Aᴅᴍɪɴs ʟɪsᴛ ʀᴇʟᴏᴀᴅᴇᴅ!</b>{self.get_owner_credit()}", parse_mode="HTML")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ MODERATION COMMANDS ─═◈═────
    async def warn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴡᴀʀɴ!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
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
            await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴡᴀʀɴ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        await db.add_warning(target.id, chat.id, reason, user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        warn_count = len(warnings)
        max_warns = Config.MAX_WARNINGS
        
        warn_msg = f"""
⚠️ <b>Wᴀʀɴɪɴɢ!</b> ⚠️

────═◈═─ ✧◈✧ ─═◈═────
👤 {target.first_name}
📊 Wᴀʀɴ: {warn_count}/{max_warns}
📝 Rᴇᴀsᴏɴ: {reason}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
        await update.message.reply_text(warn_msg, parse_mode="HTML")
        
        await self.log_action(chat.id, f"⚠️ <b>Wᴀʀɴ</b> {target.first_name} ({warn_count}/{max_warns}) ʙʏ {user.first_name} - {reason}")
        
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
🔇 <b>Aᴜᴛᴏ-Mᴜᴛᴇᴅ!</b> 🔇

────═◈═─ ✧◈✧ ─═◈═────
👤 {target.first_name}
⏱️ {mute_duration}s
📝 Rᴇᴀsᴏɴ: Exceeded warn limit
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
                await update.message.reply_text(mute_msg, parse_mode="HTML")
            except:
                pass

    # ────═◈═─ UNWARN COMMAND ─═◈═────
    async def unwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴs!")
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
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
        
        warnings = await db.get_warnings(target.id, chat.id)
        if warnings:
            await db.clear_warnings(target.id, chat.id)
            await update.message.reply_text(f"✅ <b>Rᴇᴍᴏᴠᴇᴅ ᴀʟʟ ᴡᴀʀɴs ғᴏʀ {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"✅ <b>Uɴᴡᴀʀɴ</b> {target.first_name} ʙʏ {user.first_name}")
        else:
            await update.message.reply_text(f"ℹ️ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴs!{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ WARNS COMMAND ─═◈═────
    async def warns_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
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
        
        warnings = await db.get_warnings(target.id, chat.id)
        
        if not warnings:
            await update.message.reply_text(f"✅ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs!{self.get_owner_credit()}", parse_mode="HTML")
            return
        
        warn_text = f"⚠️ <b>Wᴀʀɴɪɴɢs ғᴏʀ {target.first_name}:</b>\n\n"
        for i, warn in enumerate(warnings, 1):
            warn_text += f"└ {i}. {warn['reason']}\n"
        warn_text += self.get_owner_credit()
        
        await update.message.reply_text(warn_text, parse_mode="HTML")

    # ────═◈═─ DELWARN COMMAND ─═◈═────
    async def delwarn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        target = update.message.reply_to_message.from_user
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await context.bot.delete_message(chat.id, update.message.message_id)
        await db.add_warning(target.id, chat.id, "Deleted message", user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        
        await update.message.reply_text(f"⚠️ <b>Dᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ & ᴡᴀʀɴᴇᴅ {target.first_name}!</b> ({len(warnings)}/{Config.MAX_WARNINGS}){self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ RESETWARNS COMMAND ─═◈═────
    async def reset_warns(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇsᴇᴛ ᴡᴀʀɴs!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        await db.clear_warnings(target.id, chat.id)
        await update.message.reply_text(f"✅ <b>Rᴇsᴇᴛ ᴀʟʟ ᴡᴀʀɴs ғᴏʀ {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")

    # ────═◈═─ MUTE COMMAND ─═◈═────
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴜᴛᴇ!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴍᴜᴛᴇ ʙᴏᴛs!")
            return
        
        duration = Config.MUTE_DURATION
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            if len(context.args) > 1 and context.args[1].isdigit():
                duration = int(context.args[1])
                reason = " ".join(context.args[2:]) if len(context.args) > 2 else "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
            
            await db.add_mute(target.id, chat.id, duration, reason, user.id)
            await context.bot.restrict_chat_member(
                chat.id,
                target.id,
                ChatPermissions(can_send_messages=False)
            )
            
            mute_msg = f"""
🔇 <b>Mᴜᴛᴇᴅ!</b> 🔇

────═◈═─ ✧◈✧ ─═◈═────
👤 {target.first_name}
⏱️ {duration}s
📝 Rᴇᴀsᴏɴ: {reason}
────═◈═─ ✧◈✧ ─═◈═────
{self.get_owner_credit()}
"""
            await update.message.reply_text(mute_msg, parse_mode="HTML")
            await self.log_action(chat.id, f"🔇 <b>Mᴜᴛᴇ</b> {target.first_name} ({duration}s) ʙʏ {user.first_name} - {reason}")
            
            asyncio.create_task(self.auto_unmute(context, chat.id, target.id, duration))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ AUTO UNMUTE ─═◈═────
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

    # ────═◈═─ UNMUTE COMMAND ─═◈═────
    async def unmute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇ!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
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
            await update.message.reply_text(f"🔊 <b>Uɴᴍᴜᴛᴇᴅ {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"🔊 <b>Uɴᴍᴜᴛᴇ</b> {target.first_name} ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ KICK COMMAND ─═◈═────
    async def kick_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_mod(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴋɪᴄᴋ!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴋɪᴄᴋ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"👢 <b>Kɪᴄᴋᴇᴅ {target.first_name}!</b>\n📝 Rᴇᴀsᴏɴ: {reason}{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"👢 <b>Kɪᴄᴋ</b> {target.first_name} ʙʏ {user.first_name} - {reason}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ BAN COMMAND ─═◈═────
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʙᴀɴ!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        if target.is_bot:
            await update.message.reply_text("❌ Cᴀɴ'ᴛ ʙᴀɴ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"🚫 <b>Bᴀɴɴᴇᴅ {target.first_name}!</b>\n📝 Rᴇᴀsᴏɴ: {reason}{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"🚫 <b>Bᴀɴ</b> {target.first_name} ʙʏ {user.first_name} - {reason}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ UNBAN COMMAND ─═◈═────
    async def unban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴ!")
            return
        
        target = None
        if context.args:
            username = context.args[0].replace('@', '')
            try:
                target = await context.bot.get_chat(username)
            except:
                await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
                return
        else:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ!")
            return
        
        try:
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"✅ <b>Uɴʙᴀɴɴᴇᴅ {target.first_name}!</b>{self.get_owner_credit()}", parse_mode="HTML")
            await self.log_action(chat.id, f"✅ <b>Uɴʙᴀɴ</b> {target.first_name} ʙʏ {user.first_name}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    # ────═◈═─ APPROVE COMMAND ─═◈═────
    async def approve_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴘᴘʀᴏᴠᴇ!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        await db.approve_user(target.id, chat.id)
        await update.message.reply_text(f"✅ <b>Aᴘᴘʀᴏᴠᴇᴅ</b> {target.first_name}!\n🔗 Nᴏᴡ Yᴏᴜ Aʀᴇ Fʀᴇᴇ.{self.get_owner_credit()}", parse_mode="HTML")
        await self.log_action(chat.id, f"✅ <b>Aᴘᴘʀᴏᴠᴇ</b> {target.first_name} ʙʏ {user.first_name}")

    # ────═◈═─ UNAPPROVE COMMAND ─═◈═────
    async def unapprove_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        if not await self.is_admin(context, chat.id, user.id):
            await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ!")
            return
        
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
            return
        
        await db.unapprove_user(target.id, chat.id)
        await update.message.reply_text(f"❌ <b>Uɴᴀᴘᴘʀᴏᴠᴇᴅ</b> {target.first_name}!\n🔗 Nᴏ ᴍᴏʀᴇ ʟɪɴᴋs.{self.get_owner_credit()}", parse_mode="HTML")
        await self.log_action(chat.id, f"❌ <b>Uɴᴀᴘᴘʀᴏᴠᴇ</b> {target.first_name} ʙʏ {user.first_name}")

    # ────═◈═─ ANTI-SPAM HANDLER ─═◈═────
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
        
        if await self.is_admin(context, chat.id, user.id):
            return
        
        is_approved = await db.is_approved(user.id, chat.id)
        if is_approved:
            return
        
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        if url_pattern.search(update.message.text):
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(
                f"🔗 <b>Lɪɴᴋ Dᴇᴛᴇᴄᴛᴇᴅ!</b>\n\n{user.first_name}, ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ᴛᴏ sᴇɴᴅ ʟɪɴᴋs.\nCᴏɴᴛᴀᴄᴛ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴀᴘᴘʀᴏᴠᴀʟ.{self.get_owner_credit()}",
                parse_mode="HTML"
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
        
        if await self.is_admin(context, chat.id, user.id):
            return
        
        adult_keywords = ['porn', 'xxx', 'sex', 'nude', 'nsfw', '18+', 'adult', 'fuck', 'shit', 'bitch', 'ass']
        if any(keyword in update.message.text.lower() for keyword in adult_keywords):
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text(
                f"🔞 <b>18+ Cᴏɴᴛᴇɴᴛ Dᴇᴛᴇᴄᴛᴇᴅ!</b>\n\n{user.first_name}, ᴛʜɪs ᴛʏᴘᴇ ᴏғ ᴄᴏɴᴛᴇɴᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ.{self.get_owner_credit()}",
                parse_mode="HTML"
            )

    # ────═◈═─ CALLBACK HANDLER (FIXED) ─═◈═────
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        is_premium = user_id in Config.PREMIUM_USERS or user_id == Config.OWNER_ID
        
        # Handle main menu
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
            
            await query.edit_message_text(
                main_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Handle Stats
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
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        # Handle Settings
        elif data == "settings":
            keyboard = [
                [InlineKeyboardButton("👋 Wᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"), InlineKeyboardButton("👋 Gᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")],
                [InlineKeyboardButton("🛡️ Aɴᴛɪ-Sᴘᴀᴍ", callback_data="set_antispam"), InlineKeyboardButton("🔗 Aɴᴛɪ-Lɪɴᴋ", callback_data="set_antilink")],
                [InlineKeyboardButton("🔞 Aɴᴛɪ-18+", callback_data="set_anti18")],
                [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]
            ]
            await query.edit_message_text(
                f"⚙️ <b>Sᴇᴛᴛɪɴɢs Mᴇɴᴜ</b>\n\n{self.get_owner_credit()}",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Handle Help
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
            await query.edit_message_text(help_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        # Handle About
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
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        # Handle Staff
        elif data == "staff":
            await query.edit_message_text("👥 Uꜱᴇ /sᴛᴀғғ ᴛᴏ ᴠɪᴇᴡ sᴛᴀғғ ʟɪsᴛ!", parse_mode="HTML")
            return

        # Handle SG
        elif data == "sg":
            await query.edit_message_text(
                f"🔄 <b>SG - Uꜱᴇʀ Hɪsᴛᴏʀʏ</b>\n\n"
                f"Uꜱᴇ /sɢ @ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ\n"
                f"Tᴏ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴄᴏᴍᴘʟᴇᴛᴇ ʜɪsᴛᴏʀʏ!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
            return

        # Handle History
        elif data == "history":
            await query.edit_message_text(
                f"📜 <b>Hɪsᴛᴏʀʏ Tʀᴀᴄᴋɪɴɢ</b>\n\n"
                f"Uꜱᴇ /ʜɪsᴛᴏʀʏ @ᴜsᴇʀɴᴀᴍᴇ\n"
                f"Tᴏ ᴠɪᴇᴡ ᴛʜᴇɪʀ ᴄᴏᴍᴘʟᴇᴛᴇ ᴄʜᴀɴɢᴇ ʜɪsᴛᴏʀʏ!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
            return

        # Handle Chat
        elif data == "chat":
            await query.edit_message_text(
                f"💬 <b>Cʜᴀᴛ ᴡɪᴛʜ ᴍᴇ!</b>\n\n"
                f"Sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴀɴᴅ I'ʟʟ ʀᴇsᴘᴏɴᴅ!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
            return

        # Handle Roles
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
            await query.edit_message_text(roles_text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

        # Handle Role buttons (role_founder, role_cofounder, etc.)
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
            await query.edit_message_text(
                f"👑 <b>{role_name} Rᴏʟᴇ</b>\n\n"
                f"Tᴏ ᴀᴅᴅ ᴛʜɪs ʀᴏʟᴇ: /{role_name.lower()} @ᴜsᴇʀ\n"
                f"Tᴏ ʀᴇᴍᴏᴠᴇ ᴛʜɪs ʀᴏʟᴇ: /ᴜɴ{role_name.lower()} @ᴜsᴇʀ\n\n"
                f"<b>Dᴇsᴄʀɪᴘᴛɪᴏɴ:</b>\n{desc}{self.get_owner_credit()}",
                parse_mode="HTML"
            )
            return

        # Handle Settings toggles
        elif data.startswith("set_"):
            setting = data.replace("set_", "")
            chat_id = update.effective_chat.id
            settings = await db.get_settings(chat_id)
            current = settings.get(setting, True)
            await db.update_settings(chat_id, setting, not current)
            
            await query.edit_message_text(
                f"✅ <b>{setting.upper()}</b> {'Enabled' if not current else 'Disabled'}!{self.get_owner_credit()}",
                parse_mode="HTML"
            )
            return

        # Handle Premium
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
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
            return

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
