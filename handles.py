from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import asyncio
import datetime
import re
import io
import psutil
from datetime import datetime as dt

from config import Config
from database import Database
from utils import Utils
from keyboards import Keyboards

db = Database()
utils = Utils()

class Handlers:
    
    # ────═◈═─ GENERAL COMMANDS ─═◈═────
    
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        is_premium = await db.is_premium(user.id)
        await db.add_user(user.id, user.username, user.first_name)
        
        welcome_text = f"""
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
╰┈➤ Pʀᴇᴍɪᴜᴍ Fᴇᴀᴛᴜʀᴇs  

👑 <b>Oᴡɴᴇʀ:</b>  
╰┈➤ {Config.OWNER_NAME} ({Config.OWNER_USERNAME})

📢 <b>Usᴇ /help ғᴏʀ ᴄᴏᴍᴍᴀɴᴅs</b>
"""
        keyboard = Keyboards.main_menu(is_premium)
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    
    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = f"""
📖 <b>Cᴏᴍᴍᴀɴᴅ Lɪsᴛ</b> 📖

╔═══════════════════════════════════════╗

<b>👑 Aᴅᴍɪɴ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /warn @user - Wᴀʀɴ ᴜsᴇʀ
╰┈➤ /unwarn @user - Rᴇᴍᴏᴠᴇ ᴡᴀʀɴs
╰┈➤ /warns @user - Cʜᴇᴄᴋ ᴡᴀʀɴs
╰┈➤ /delwarn - Dᴇʟᴇᴛᴇ & ᴡᴀʀɴ
╰┈➤ /resetwarns @user - Rᴇsᴇᴛ ᴡᴀʀɴs
╰┈➤ /mute @user - Mᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /unmute @user - Uɴᴍᴜᴛᴇ ᴜsᴇʀ
╰┈➤ /kick @user - Kɪᴄᴋ ᴜsᴇʀ
╰┈➤ /ban @user - Bᴀɴ ᴜsᴇʀ
╰┈➤ /unban @user - Uɴʙᴀɴ ᴜsᴇʀ
╰┈➤ /approve @user - Aᴘᴘʀᴏᴠᴇ ᴜsᴇʀ
╰┈➤ /unapprove @user - Rᴇᴠᴏᴋᴇ ᴀᴘᴘʀᴏᴠᴀʟ
╰┈➤ /settings - Mᴀɴᴀɢᴇ sᴇᴛᴛɪɴɢs
╰┈➤ /reload - Rᴇʟᴏᴀᴅ ᴀᴅᴍɪɴs

<b>📌 Pɪɴ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /pin - Pɪɴ ᴍᴇssᴀɢᴇ
╰┈➤ /unpin - Uɴᴘɪɴ
╰┈➤ /pinned - Vɪᴇᴡ ᴘɪɴɴᴇᴅ
╰┈➤ /editpin - Eᴅɪᴛ ᴘɪɴɴᴇᴅ
╰┈➤ /delpin - Dᴇʟᴇᴛᴇ ᴘɪɴ

<b>🗑️ Dᴇʟᴇᴛᴇ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /del - Dᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ
╰┈➤ /logdel - Dᴇʟᴇᴛᴇ & ʟᴏɢ
╰┈➤ /purge - Cʟᴇᴀʀ ᴍᴜʟᴛɪᴘʟᴇ

<b>👑 Rᴏʟᴇ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /cofounder @user - Aᴅᴅ Cᴏ-Fᴏᴜɴᴅᴇʀ
╰┈➤ /uncofounder @user - Rᴇᴍᴏᴠᴇ Cᴏ-Fᴏᴜɴᴅᴇʀ
╰┈➤ /mod @user - Aᴅᴅ Mᴏᴅᴇʀᴀᴛᴏʀ
╰┈➤ /unmod @user - Rᴇᴍᴏᴠᴇ Mᴏᴅᴇʀᴀᴛᴏʀ
╰┈➤ /muter @user - Aᴅᴅ Mᴜᴛᴇʀ
╰┈➤ /unmuter @user - Rᴇᴍᴏᴠᴇ Mᴜᴛᴇʀ
╰┈➤ /cleaner @user - Aᴅᴅ Cʟᴇᴀɴᴇʀ
╰┈➤ /uncleaner @user - Rᴇᴍᴏᴠᴇ Cʟᴇᴀɴᴇʀ
╰┈➤ /helper @user - Aᴅᴅ Hᴇʟᴘᴇʀ
╰┈➤ /unhelper @user - Rᴇᴍᴏᴠᴇ Hᴇʟᴘᴇʀ
╰┈➤ /free @user - Aᴅᴅ Fʀᴇᴇ
╰┈➤ /unfree @user - Rᴇᴍᴏᴠᴇ Fʀᴇᴇ

<b>📊 Gᴇɴᴇʀᴀʟ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /start - Sᴛᴀʀᴛ ʙᴏᴛ
╰┈➤ /help - Gᴇᴛ ʜᴇʟᴘ
╰┈➤ /about - Aʙᴏᴜᴛ ʙᴏᴛ
╰┈➤ /ping - Cʜᴇᴄᴋ ʙᴏᴛ
╰┈➤ /staff - Vɪᴇᴡ sᴛᴀғғ
╰┈➤ /info @user - Uꜱᴇʀ ɪɴғᴏ
╰┈➤ /infopvt @user - Uꜱᴇʀ ɪɴғᴏ ᴘʀɪᴠᴀᴛᴇ
╰┈➤ /me - Yᴏᴜʀ ɪɴғᴏ
╰┈➤ /geturl - Gᴇᴛ ʟɪɴᴋ
╰┈➤ /sg @user - Vɪᴇᴡ ʜɪsᴛᴏʀʏ
╰┈➤ /history @user - Exᴘᴏʀᴛ ʜɪsᴛᴏʀʏ
╰┈➤ /chat - Cʜᴀᴛ ᴡɪᴛʜ ʙᴏᴛ
╰┈➤ /roles - Vɪᴇᴡ ʀᴏʟᴇs
╰┈➤ /premium - Cʜᴇᴄᴋ ᴘʀᴇᴍɪᴜᴍ

<b>🔰 Fɪʟᴛᴇʀ Cᴏᴍᴍᴀɴᴅs:</b>
╰┈➤ /filter ᴋᴇʏ ʀᴇᴘʟʏ - Aᴅᴅ ғɪʟᴛᴇʀ
╰┈➤ /stopfilter ᴋᴇʏ - Rᴇᴍᴏᴠᴇ ғɪʟᴛᴇʀ
╰┈➤ /filters - Lɪsᴛ ғɪʟᴛᴇʀs

<b>👋 Wᴇʟᴄᴏᴍᴇ:</b>
╰┈➤ /enablewelcome - Eɴᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ
╰┈➤ /disablewelcome - Dɪsᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ

╚═══════════════════════════════════════╝

🔥 Pᴏᴡᴇʀᴇᴅ ʙʏ {Config.BOT_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command"""
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

⚙️ <b>Fᴇᴀᴛᴜʀᴇs:</b>
╰┈➤ Aɴᴛɪ-Sᴘᴀᴍ
╰┈➤ Aɴᴛɪ-Lɪɴᴋ
╰┈➤ Aɴᴛɪ-18+
╰┈➤ Wᴀʀɴ Sʏsᴛᴇᴍ
╰┈➤ Mᴜᴛᴇ/Uɴᴍᴜᴛᴇ
╰┈➤ Bᴀɴ/Kɪᴄᴋ
╰┈➤ Pɪɴ/Uɴᴘɪɴ
╰┈➤ Dᴇʟᴇᴛᴇ/Pᴜʀɢᴇ
╰┈➤ Rᴏʟᴇs Sʏsᴛᴇᴍ

📢 <b>Vᴇʀsɪᴏɴ:</b> 3.0.0
🔰 <b>Sᴛᴀᴛᴜs:</b> Aᴄᴛɪᴠᴇ

👑 <b>Bʏ:</b> {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ping command"""
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
            boot_time = dt.fromtimestamp(psutil.boot_time())
            uptime = dt.now() - boot_time
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
        
        start_time = dt.now()
        msg = await update.message.reply_text("🏓 Pɪɴɢɪɴɢ...")
        end_time = dt.now()
        latency = (end_time - start_time).microseconds / 1000
        
        text = f"""
⚡️ <b>{Config.BOT_NAME}</b>

🏓 ᴘɪɴɢ..ᴩᴏɴɢ : <code>{latency:.3f}ᴍs</code>

» <b>sʏsᴛᴇᴍ sᴛᴀᴛs :</b>

:⧽ ᴜᴩᴛɪᴍᴇ : <code>{uptime_str}</code>
:⧽ ʀᴀᴍ : <code>{ram_used:.2f}GB / {ram_total:.2f}GB</code> ({ram_percent}%)
:⧽ ᴄᴩᴜ : <code>{cpu_usage}%</code>
:⧽ ᴅɪsᴋ : <code>{disk_used:.2f}GB / {disk_total:.2f}GB</code> ({disk_percent}%)

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        await msg.edit_text(text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def staff_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /staff command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
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
            
            # Get custom roles from database
            staff_roles = await db.get_all_staff(chat.id)
            
            text = f"""
👥 <b>Sᴛᴀғғ Lɪsᴛ</b> 👥

────═◈═─ ✧◈✧ ─═◈═────
👑 <b>Oᴡɴᴇʀ:</b>
╰┈➤ {owner.first_name} (@{owner.username if owner.username else 'N/A'})

👔 <b>Aᴅᴍɪɴs: ({len(admin_list)})</b>
"""
            for admin in admin_list:
                text += f"╰┈➤ {admin.first_name} (@{admin.username if admin.username else 'N/A'})\n"
            
            if staff_roles:
                text += f"\n<b>⭐ Cᴜsᴛᴏᴍ Rᴏʟᴇs:</b>\n"
                for member in staff_roles:
                    user = await db.get_user(member["user_id"])
                    if user:
                        text += f"╰┈➤ {user.get('first_name', 'Unknown')} - <i>{member['role']}</i>\n"
            
            text += f"\n📊 <b>Tᴏᴛᴀʟ Sᴛᴀғғ:</b> {len(admin_list) + 1 + len(staff_roles)}"
            
            keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
            await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command"""
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
            bio = getattr(user_full, 'bio', 'N/A')
            stats = await db.get_user_stats(target.id)
            role = await db.get_user_role(target.id, update.effective_chat.id) if update.effective_chat.type in ['group', 'supergroup'] else "N/A"
            
            text = f"""
📋 <b>Uꜱᴇʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Nᴀᴍᴇ:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{target.username if target.username else 'N/A'}
📝 <b>Bɪᴏ:</b> {bio[:100] if bio != 'N/A' else 'N/A'}
🔰 <b>Rᴏʟᴇ:</b> {role}
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
⚠️ <b>Wᴀʀɴs:</b> {stats.get('warns', 0)}
────═◈═─ ✧◈✧ ─═◈═────

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def infopvt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /infopvt command"""
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
            bio = getattr(user_full, 'bio', 'N/A')
            stats = await db.get_user_stats(target.id)
            
            text = f"""
📋 <b>Uꜱᴇʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Nᴀᴍᴇ:</b> {target.first_name}
🆔 <b>ID:</b> <code>{target.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{target.username if target.username else 'N/A'}
📝 <b>Bɪᴏ:</b> {bio[:100] if bio != 'N/A' else 'N/A'}
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
⚠️ <b>Wᴀʀɴs:</b> {stats.get('warns', 0)}
────═◈═─ ✧◈✧ ─═◈═────

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            await context.bot.send_message(update.effective_user.id, text, parse_mode=ParseMode.HTML)
            await update.message.reply_text("✅ Iɴғᴏʀᴍᴀᴛɪᴏɴ sᴇɴᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ!")
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def me_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /me command"""
        user = update.effective_user
        chat = update.effective_chat
        
        warnings = await db.get_warnings(user.id, chat.id) if chat.type in ['group', 'supergroup'] else []
        stats = await db.get_user_stats(user.id)
        role = await db.get_user_role(user.id, chat.id) if chat.type in ['group', 'supergroup'] else "N/A"
        
        text = f"""
📋 <b>Yᴏᴜʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ</b>

────═◈═─ ✧◈✧ ─═◈═────
👤 <b>Nᴀᴍᴇ:</b> {user.first_name}
🆔 <b>ID:</b> <code>{user.id}</code>
📛 <b>Uꜱᴇʀɴᴀᴍᴇ:</b> @{user.username if user.username else 'N/A'}
🔰 <b>Rᴏʟᴇ:</b> {role}
📊 <b>Mᴇssᴀɢᴇs:</b> {stats.get('messages', 0)}
⚠️ <b>Wᴀʀɴs:</b> {len(warnings)}
────═◈═─ ✧◈✧ ─═◈═────

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def geturl_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /geturl command"""
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        chat = update.effective_chat
        msg = update.message.reply_to_message
        link = f"https://t.me/{chat.username}/{msg.message_id}" if chat.username else f"https://t.me/c/{str(chat.id)[4:]}/{msg.message_id}"
        await update.message.reply_text(f"🔗 <b>Mᴇssᴀɢᴇ Lɪɴᴋ:</b>\n{link}", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def sg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sg command - User history"""
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ!")
            return
        
        history = await db.get_user_history(target.id)
        
        if not history:
            await update.message.reply_text(f"📋 Nᴏ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ ғᴏʀ {target.first_name}!", parse_mode=ParseMode.HTML)
            return
        
        text = f"""
🔄 <b>Uꜱᴇʀ Hɪsᴛᴏʀʏ - {target.first_name}</b>

<b>Username:</b> @{target.username if target.username else 'N/A'}
<b>ID:</b> <code>{target.id}</code>
<b>Tᴏᴛᴀʟ Cʜᴀɴɢᴇs:</b> {len(history)}

────═◈═─ ✧◈✧ ─═◈═────
"""
        count = 0
        for entry in history[:10]:
            count += 1
            timestamp = entry.get('timestamp', 'Unknown')
            text += f"└ {count}. Nᴀᴍᴇ: {entry.get('first_name', 'N/A')} | Usᴇʀɴᴀᴍᴇ: @{entry.get('username', 'N/A')} ({timestamp})\n"
        
        if len(history) > 10:
            text += f"\n... ᴀɴᴅ {len(history) - 10} ᴍᴏʀᴇ ᴇɴᴛʀɪᴇs"
        
        text += f"\n\n:⧽ ʙʏ » {Config.OWNER_NAME}"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command - Export history as file"""
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
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ!")
            return
        
        history = await db.get_user_history(target.id)
        
        if not history:
            await update.message.reply_text(f"📋 Nᴏ ʜɪsᴛᴏʀʏ ғᴏᴜɴᴅ ғᴏʀ {target.first_name}!", parse_mode=ParseMode.HTML)
            return
        
        # Create file content
        file_content = f"""
╔═══════════════════════════════════════════════════════════╗
║          USER HISTORY REPORT - {target.first_name}          ║
╚═══════════════════════════════════════════════════════════╝

Username: @{target.username if target.username else 'N/A'}
User ID: {target.id}
Total Changes: {len(history)}

═══════════════════════════════════════════════════════════════

"""
        for i, entry in enumerate(history, 1):
            file_content += f"""
┌─ Entry #{i}
├─ First Name: {entry.get('first_name', 'N/A')}
├─ Last Name: {entry.get('last_name', 'N/A')}
├─ Username: @{entry.get('username', 'N/A')}
└─ Timestamp: {entry.get('timestamp', 'Unknown')}
{'─' * 50}
"""
        
        file_content += f"""
═══════════════════════════════════════════════════════════════
Report Generated By: {Config.BOT_NAME}
Generated On: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}
:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        
        # Send as file
        file = io.BytesIO(file_content.encode('utf-8'))
        file.name = f"history_{target.id}_{dt.now().strftime('%Y%m%d')}.txt"
        
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=file,
            caption=f"📜 <b>Hɪsᴛᴏʀʏ Rᴇᴘᴏʀᴛ - {target.first_name}</b>",
            parse_mode=ParseMode.HTML
        )
    
    @staticmethod
    async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chat command"""
        text = f"""
💬 <b>Cʜᴀᴛ ᴡɪᴛʜ Mᴇ!</b>

Yᴏᴜ ᴄᴀɴ sᴇɴᴅ ᴍᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴀɴᴅ I'ʟʟ ʀᴇsᴘᴏɴᴅ!

<b>Wʜᴀᴛ I ᴄᴀɴ ᴅᴏ:</b>
╰┈➤ Aɴsᴡᴇʀ ǫᴜᴇsᴛɪᴏɴs
╰┈➤ Pʀᴏᴠɪᴅᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ
╰┈➤ Hᴀᴠᴇ ᴀ ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ

Jᴜsᴛ ᴛʏᴘᴇ ᴀɴʏᴛʜɪɴɢ!
:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def roles_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /roles command"""
        text = f"""
👑 <b>Uꜱᴇʀ Rᴏʟᴇs</b> 👑

<b>Fᴏᴜɴᴅᴇʀ:</b> Gʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ - Aʟʟ ᴘᴏᴡᴇʀs
<b>Cᴏ-Fᴏᴜɴᴅᴇʀ:</b> Mᴀɴᴀɢᴇs sᴛᴀғғ
<b>Aᴅᴍɪɴ:</b> Gʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ
<b>Mᴏᴅᴇʀᴀᴛᴏʀ:</b> Mᴏᴅᴇʀᴀᴛᴇs ᴜsᴇʀs
<b>Mᴜᴛᴇʀ:</b> Cᴀɴ ᴍᴜᴛᴇ ᴜsᴇʀs
<b>Cʟᴇᴀɴᴇʀ:</b> Cᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs
<b>Hᴇʟᴘᴇʀ:</b> Aᴘᴘᴇᴀʀs ɪɴ sᴛᴀғғ
<b>Fʀᴇᴇ:</b> Iɢɴᴏʀᴇᴅ ʙʏ ᴀᴜᴛᴏ-ᴘᴜɴɪsʜᴍᴇɴᴛ

Uꜱᴇ /help ᴛᴏ sᴇᴇ ʀᴏʟᴇ ᴄᴏᴍᴍᴀɴᴅs!
:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    
    @staticmethod
    async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /premium command"""
        user = update.effective_user
        is_premium = await db.is_premium(user.id)
        
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

:⧽ ʙʏ » {Config.OWNER_NAME}
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

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        keyboard = [[InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="main_menu")]]
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))
    
    # ────═◈═─ WELCOME SETTINGS ─═◈═────
    
    @staticmethod
    async def enable_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enable welcome messages"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!")
                return
        except:
            return
        
        await db.update_settings(chat.id, "welcome", True)
        await update.message.reply_text("✅ <b>Wᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ!</b>", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def disable_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disable welcome messages"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!")
                return
        except:
            return
        
        await db.update_settings(chat.id, "welcome", False)
        await update.message.reply_text("❌ <b>Wᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ!</b>", parse_mode=ParseMode.HTML)
    
    # ────═◈═─ WELCOME/GIODBYE HANDLERS ─═◈═────
    
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
            
            await db.add_user(member.id, member.username, member.first_name)
            
            try:
                member_count = await context.bot.get_chat_member_count(chat.id)
            except:
                member_count = "?"
            
            welcome_msg = f"""
👋 <b>Wᴇʟᴄᴏᴍᴇ Tᴏ Tʜᴇ Pᴀʀᴛʏ!</b> 🎉

<b>Nᴀᴍᴇ:</b> {member.first_name}
<b>Gʀᴏᴜᴘ:</b> {chat.title}
<b>Mᴇᴍʙᴇʀs:</b> {member_count}

🌟 <b>Pʀᴏᴛᴇᴄᴛᴇᴅ Bʏ {Config.BOT_NAME}</b>
:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            
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
💔 <b>Gᴏᴏᴅʙʏᴇ!</b> 💔

<b>Uꜱᴇʀ:</b> {member.first_name}
📍 <b>Gʀᴏᴜᴘ:</b> {chat.title}

😢 Wᴇ ᴡɪʟʟ ᴍɪss ʏᴏᴜ!
:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        await context.bot.send_message(
            chat.id,
            goodbye_msg,
            parse_mode=ParseMode.HTML
        )
    
    # ────═◈═─ SETTINGS & RELOAD ─═◈═────
    
    @staticmethod
    async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴠɪᴇᴡ sᴇᴛᴛɪɴɢs!")
                return
        except:
            return
        
        keyboard = Keyboards.settings_menu()
        await update.message.reply_text(
            f"⚙️ <b>Sᴇᴛᴛɪɴɢs Mᴇɴᴜ</b>\n\n:⧽ ʙʏ » {Config.OWNER_NAME}",
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    
    @staticmethod
    async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reload command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇʟᴏᴀᴅ!")
                return
        except:
            return
        
        try:
            admins = await context.bot.get_chat_administrators(chat.id)
            admin_ids = [admin.user.id for admin in admins]
            await db.update_settings(chat.id, "admins", admin_ids)
            await update.message.reply_text("✅ <b>Aᴅᴍɪɴs ʟɪsᴛ ʀᴇʟᴏᴀᴅᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    # ────═◈═─ MODERATION COMMANDS ─═◈═────
    
    @staticmethod
    async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warn command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴡᴀʀɴ!")
                return
        except:
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ʀᴇᴘʟʏ!")
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
        
        if not target or target.is_bot:
            await update.message.reply_text("❌ Cᴀɴ'ᴛ ᴡᴀʀɴ ʙᴏᴛs!")
            return
        
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        await db.add_warning(target.id, chat.id, reason, user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        warn_count = len(warnings)
        settings = await db.get_settings(chat.id)
        max_warns = settings.get('warn_limit', 3)
        
        text = f"""
⚠️ <b>Wᴀʀɴɪɴɢ!</b> ⚠️

<b>Uꜱᴇʀ:</b> {target.first_name}
<b>Wᴀʀɴ:</b> {warn_count}/{max_warns}
<b>Rᴇᴀsᴏɴ:</b> {reason}

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        if warn_count >= max_warns:
            await update.message.reply_text(f"⚠️ {target.first_name} ʜᴀs ʀᴇᴀᴄʜᴇᴅ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ! Tʜᴇʏ ᴡɪʟʟ ʙᴇ ᴍᴜᴛᴇᴅ.", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def unwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unwarn command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴡᴀʀɴ!")
                return
        except:
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
        
        await db.clear_warnings(target.id, chat.id)
        await update.message.reply_text(f"✅ <b>Rᴇᴍᴏᴠᴇᴅ ᴀʟʟ ᴡᴀʀɴs ғᴏʀ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /warns command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
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
            await update.message.reply_text(f"✅ {target.first_name} ʜᴀs ɴᴏ ᴡᴀʀɴɪɴɢs!", parse_mode=ParseMode.HTML)
            return
        
        text = f"⚠️ <b>Wᴀʀɴɪɴɢs ғᴏʀ {target.first_name}:</b>\n\n"
        for i, warn in enumerate(warnings, 1):
            text += f"└ {i}. {warn['reason']}\n"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def delwarn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delwarn command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!")
                return
        except:
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        target = update.message.reply_to_message.from_user
        await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
        await db.add_warning(target.id, chat.id, "Dᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ", user.id)
        warnings = await db.get_warnings(target.id, chat.id)
        
        await update.message.reply_text(f"⚠️ <b>Dᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇ & ᴡᴀʀɴᴇᴅ {target.first_name}!</b> ({len(warnings)}/3)", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def resetwarns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /resetwarns command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇsᴇᴛ ᴡᴀʀɴs!")
                return
        except:
            return
        
        if not context.args and not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀ!")
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
        await update.message.reply_text(f"✅ <b>Rᴇsᴇᴛ ᴀʟʟ ᴡᴀʀɴs ғᴏʀ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mute command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴍᴜᴛᴇ!")
                return
        except:
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
        reason = "Nᴏ ʀᴇᴀsᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ"
        
        try:
            if len(context.args) > 1:
                try:
                    duration = int(context.args[1])
                    if len(context.args) > 2:
                        reason = " ".join(context.args[2:])
                except:
                    reason = " ".join(context.args[1:])
            
            await db.add_mute(target.id, chat.id, duration, reason, user.id)
            await context.bot.restrict_chat_member(chat.id, target.id, ChatPermissions(can_send_messages=False))
            
            text = f"""
🔇 <b>Mᴜᴛᴇᴅ!</b> 🔇

<b>Uꜱᴇʀ:</b> {target.first_name}
<b>Dᴜʀᴀᴛɪᴏɴ:</b> {duration}s
<b>Rᴇᴀsᴏɴ:</b> {reason}

:⧽ ʙʏ » {Config.OWNER_NAME}
"""
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            
            async def auto_unmute():
                await asyncio.sleep(duration)
                await db.remove_mute(target.id, chat.id)
                try:
                    await context.bot.restrict_chat_member(chat.id, target.id, ChatPermissions(can_send_messages=True))
                except:
                    pass
            
            asyncio.create_task(auto_unmute())
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unmute command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴍᴜᴛᴇ!")
                return
        except:
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
            await context.bot.restrict_chat_member(chat.id, target.id, ChatPermissions(can_send_messages=True))
            await update.message.reply_text(f"🔊 <b>Uɴᴍᴜᴛᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /kick command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴋɪᴄᴋ!")
                return
        except:
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
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"👢 <b>Kɪᴄᴋᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ban command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʙᴀɴ!")
                return
        except:
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
        
        try:
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"🚫 <b>Bᴀɴɴᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unban command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴʙᴀɴ!")
                return
        except:
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ!")
            return
        
        username = context.args[0].replace('@', '')
        try:
            target = await context.bot.get_chat(username)
        except:
            await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        try:
            await context.bot.unban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"✅ <b>Uɴʙᴀɴɴᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴘᴘʀᴏᴠᴇ!")
                return
        except:
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
        await update.message.reply_text(f"✅ <b>Aᴘᴘʀᴏᴠᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def unapprove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unapprove command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴀᴘᴘʀᴏᴠᴇ!")
                return
        except:
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
        await update.message.reply_text(f"❌ <b>Uɴᴀᴘᴘʀᴏᴠᴇᴅ {target.first_name}!</b>", parse_mode=ParseMode.HTML)
    
    # ────═◈═─ ROLE COMMANDS ─═◈═────
    
    @staticmethod
    async def cofounder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._add_role(update, context, "Co-Founder")
    
    @staticmethod
    async def uncofounder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._remove_role(update, context, "Co-Founder")
    
    @staticmethod
    async def mod_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._add_role(update, context, "Moderator")
    
    @staticmethod
    async def unmod_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._remove_role(update, context, "Moderator")
    
    @staticmethod
    async def muter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._add_role(update, context, "Muter")
    
    @staticmethod
    async def unmuter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._remove_role(update, context, "Muter")
    
    @staticmethod
    async def cleaner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._add_role(update, context, "Chat Cleaner")
    
    @staticmethod
    async def uncleaner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._remove_role(update, context, "Chat Cleaner")
    
    @staticmethod
    async def helper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._add_role(update, context, "Helper")
    
    @staticmethod
    async def unhelper_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._remove_role(update, context, "Helper")
    
    @staticmethod
    async def free_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._add_role(update, context, "Free")
    
    @staticmethod
    async def unfree_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await Handlers._remove_role(update, context, "Free")
    
    # ────═◈═─ ROLE HELPER METHODS ─═◈═────
    
    @staticmethod
    async def _add_role(update: Update, context: ContextTypes.DEFAULT_TYPE, role: str):
        """Helper method to add role"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴅᴅ ʀᴏʟᴇs!")
                return
        except:
            return
        
        if not context.args:
            await update.message.reply_text(f"⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ!\nᴇxᴀᴍᴘʟᴇ: /{role.lower().replace(' ', '')} @ᴜsᴇʀ")
            return
        
        username = context.args[0].replace('@', '')
        try:
            target = await context.bot.get_chat(username)
        except:
            await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        await db.set_user_role(target.id, chat.id, role)
        await update.message.reply_text(f"✅ <b>{role}</b> ʀᴏʟᴇ ᴀᴅᴅᴇᴅ ᴛᴏ {target.first_name}!", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def _remove_role(update: Update, context: ContextTypes.DEFAULT_TYPE, role: str):
        """Helper method to remove role"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ʀᴏʟᴇs!")
                return
        except:
            return
        
        if not context.args:
            await update.message.reply_text(f"⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴜsᴇʀɴᴀᴍᴇ!\nᴇxᴀᴍᴘʟᴇ: /un{role.lower().replace(' ', '')} @ᴜsᴇʀ")
            return
        
        username = context.args[0].replace('@', '')
        try:
            target = await context.bot.get_chat(username)
        except:
            await update.message.reply_text("❌ Uꜱᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ!")
            return
        
        await db.remove_user_role(target.id, chat.id)
        await update.message.reply_text(f"❌ <b>{role}</b> ʀᴏʟᴇ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ {target.first_name}!", parse_mode=ParseMode.HTML)
    
    # ────═◈═─ PIN COMMANDS ─═◈═────
    
    @staticmethod
    async def pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pin command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘɪɴ ᴍᴇssᴀɢᴇs!")
                return
        except:
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ!")
            return
        
        try:
            await context.bot.pin_chat_message(
                chat.id,
                update.message.reply_to_message.message_id,
                disable_notification=True
            )
            await update.message.reply_text("📌 <b>Mᴇssᴀɢᴇ ᴘɪɴɴᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unpin command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜɴᴘɪɴ ᴍᴇssᴀɢᴇs!")
                return
        except:
            return
        
        try:
            await context.bot.unpin_chat_message(chat.id)
            await update.message.reply_text("📌 <b>Mᴇssᴀɢᴇ ᴜɴᴘɪɴɴᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def pinned_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pinned command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        
        try:
            pinned = await context.bot.get_chat(chat.id)
            if pinned.pinned_message:
                text = f"""
📌 <b>Cᴜʀʀᴇɴᴛ Pɪɴɴᴇᴅ Mᴇssᴀɢᴇ</b>

<b>Fʀᴏᴍ:</b> {pinned.pinned_message.from_user.first_name}
<b>Dᴀᴛᴇ:</b> {pinned.pinned_message.date.strftime('%Y-%m-%d %H:%M:%S')}

<b>Mᴇssᴀɢᴇ:</b>
{pinned.pinned_message.text[:500] if pinned.pinned_message.text else '📎 Mᴇᴅɪᴀ ᴍᴇssᴀɢᴇ'}
"""
                await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            else:
                await update.message.reply_text("📌 <b>Nᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def editpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /editpin command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇᴅɪᴛ ᴘɪɴs!")
                return
        except:
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴇᴅɪᴛ ᴘɪɴ!")
            return
        
        try:
            await context.bot.unpin_chat_message(chat.id)
            await context.bot.pin_chat_message(
                chat.id,
                update.message.reply_to_message.message_id,
                disable_notification=True
            )
            await update.message.reply_text("📌 <b>Pɪɴ ᴜᴘᴅᴀᴛᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def delpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delpin command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴘɪɴs!")
                return
        except:
            return
        
        try:
            await context.bot.unpin_chat_message(chat.id)
            await update.message.reply_text("🗑️ <b>Pɪɴ ᴅᴇʟᴇᴛᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    # ────═◈═─ DELETE COMMANDS ─═◈═────
    
    @staticmethod
    async def del_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /del command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs!")
                return
        except:
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ!")
            return
        
        try:
            await context.bot.delete_message(chat.id, update.message.reply_to_message.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def logdel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logdel command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs!")
                return
        except:
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ!")
            return
        
        msg = update.message.reply_to_message
        target = msg.from_user
        
        # Log the deletion
        log_text = f"""
🗑️ <b>Mᴇssᴀɢᴇ Dᴇʟᴇᴛᴇᴅ!</b>

<b>Dᴇʟᴇᴛᴇᴅ ʙʏ:</b> {user.first_name}
<b>Mᴇssᴀɢᴇ ғʀᴏᴍ:</b> {target.first_name}
<b>Cʜᴀᴛ:</b> {chat.title}
<b>Mᴇssᴀɢᴇ:</b>
{msg.text[:300] if msg.text else '📎 Mᴇᴅɪᴀ ᴍᴇssᴀɢᴇ'}
"""
        
        try:
            # Try to send log to log channel
            await context.bot.send_message(
                Config.LOG_CHANNEL,
                log_text,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        
        try:
            await context.bot.delete_message(chat.id, msg.message_id)
            await context.bot.delete_message(chat.id, update.message.message_id)
            await update.message.reply_text("✅ <b>Mᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ & ʟᴏɢɢᴇᴅ!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    @staticmethod
    async def purge_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /purge command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴘᴜʀɢᴇ!")
                return
        except:
            return
        
        if not update.message.reply_to_message:
            await update.message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ sᴛᴀʀᴛɪɴɢ ᴍᴇssᴀɢᴇ!")
            return
        
        start_msg = update.message.reply_to_message
        current_msg = update.message
        
        try:
            # Delete messages from start to current
            for i in range(start_msg.message_id, current_msg.message_id + 1):
                try:
                    await context.bot.delete_message(chat.id, i)
                except:
                    pass
            
            await update.message.reply_text(f"🧹 <b>Pᴜʀɢᴇᴅ {current_msg.message_id - start_msg.message_id + 1} ᴍᴇssᴀɢᴇs!</b>", parse_mode=ParseMode.HTML)
        except Exception as e:
            await update.message.reply_text(f"❌ Eʀʀᴏʀ: {str(e)}")
    
    # ────═◈═─ FILTER COMMANDS ─═◈═────
    
    @staticmethod
    async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /filter command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴀᴅᴅ ғɪʟᴛᴇʀs!")
                return
        except:
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("⚠️ Usᴀɢᴇ: /filter ᴋᴇʏᴡᴏʀᴅ ʀᴇᴘʟʏ ᴛᴇxᴛ")
            return
        
        keyword = context.args[0].lower()
        reply_text = " ".join(context.args[1:])
        
        await db.add_filter(chat.id, keyword, reply_text)
        await update.message.reply_text(f"✅ <b>Fɪʟᴛᴇʀ ᴀᴅᴅᴇᴅ!</b>\n\n<b>Kᴇʏᴡᴏʀᴅ:</b> {keyword}\n<b>Rᴇᴘʟʏ:</b> {reply_text}", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def stopfilter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stopfilter command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        user = update.effective_user
        chat = update.effective_chat
        
        try:
            member = await context.bot.get_chat_member(chat.id, user.id)
            if not member.status in ['administrator', 'creator']:
                await update.message.reply_text("❌ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ғɪʟᴛᴇʀs!")
                return
        except:
            return
        
        if not context.args:
            await update.message.reply_text("⚠️ Usᴀɢᴇ: /stopfilter ᴋᴇʏᴡᴏʀᴅ")
            return
        
        keyword = context.args[0].lower()
        result = await db.remove_filter(chat.id, keyword)
        
        if result:
            await update.message.reply_text(f"✅ <b>Fɪʟᴛᴇʀ ʀᴇᴍᴏᴠᴇᴅ!</b>\n\n<b>Kᴇʏᴡᴏʀᴅ:</b> {keyword}", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"❌ Fɪʟᴛᴇʀ <b>{keyword}</b> ɴᴏᴛ ғᴏᴜɴᴅ!", parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def filters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /filters command"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            await update.message.reply_text("❌ Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs!")
            return
        
        chat = update.effective_chat
        
        filters_list = await db.get_filters(chat.id)
        
        if not filters_list:
            await update.message.reply_text("📋 <b>Nᴏ ғɪʟᴛᴇʀs ᴀᴄᴛɪᴠᴇ!</b>", parse_mode=ParseMode.HTML)
            return
        
        text = f"📋 <b>Aᴄᴛɪᴠᴇ Fɪʟᴛᴇʀs ({len(filters_list)})</b>\n\n"
        for f in filters_list:
            text += f"└ <b>{f['keyword']}</b> - {f['reply_text'][:50]}...\n"
        
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    
    @staticmethod
    async def filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle filter auto-reply"""
        if not update.effective_chat.type in ['group', 'supergroup']:
            return
        
        if not update.message.text:
            return
        
        chat = update.effective_chat
        text = update.message.text.lower()
        
        filters_list = await db.get_filters(chat.id)
        
        for f in filters_list:
            if f['keyword'].lower() in text:
                try:
                    await update.message.reply_text(f['reply_text'])
                except:
                    pass
                break
