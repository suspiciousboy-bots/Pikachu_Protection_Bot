import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Token
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # MongoDB URI
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "pikachu_protection")
    
    # Admin IDs (Owner) - Your ID: 7790607144
    OWNER_ID = [int(id) for id in os.getenv("OWNER_ID", "7790607144").split(",") if id]
    
    # Bot Info - Your Custom Details
    BOT_NAME = "── ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ──"
    BOT_USERNAME = "@Pikachu_Protection_Robot"
    OWNER_NAME = "⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐"
    OWNER_USERNAME = "@CrazyyCore"
    
    # Protection Settings
    WELCOME_DELETE_AFTER = 30  # seconds
    MAX_WARNINGS = 3
    MUTE_DURATION = 300  # seconds
    
    # Channels/Logs
    LOG_CHANNEL = os.getenv("LOG_CHANNEL", "-1003424504397")  # Channel ID for logs
    
    # Anti-Spam Settings
    FLOOD_LIMIT = 5  # messages per second
    FLOOD_WARNINGS = 2
    
    # Premium Features - Your ID: 7790607144
    PREMIUM_USERS = [int(id) for id in os.getenv("PREMIUM_USERS", "7790607144").split(",") if id]

class Messages:
    # Premium Styled Messages
    WELCOME = """
✨ **ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ᴘᴀʀᴛʏ!** ✨

────═◈═─ ✧◈✧ ─═◈═────
  🎯 {user_mention}     
  📍 {group_name}       
  👥 {member_count}     
✦•····················•✦

🌟 **ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ:**  
╰┈➤ {bot_name}

💫 **ʀᴜʟᴇs:**  
╰┈➤ ᴅᴏɴ'ᴛ sᴘᴀᴍ  
╰┈➤ ɴᴏ ᴀʙᴜsᴇ  
╰┈➤ ɴᴏ ᴘᴏʀɴ  

🔰 **ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴡᴇʟᴄᴏᴍᴇᴅ** 🔰
"""
    
    GOODBYE = """
💔 **ɢᴏᴏᴅʙʏᴇ!** 💔

────═◈═─ ✧◈✧ ─═◈═────
  👋 {user_mention}     
  🚪 ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ   
  📍 {group_name}      
✦•····················•✦

😢 ᴡᴇ ᴡɪʟʟ ᴍɪss ʏᴏᴜ!
"""
    
    WARN = """
⚠️ **ᴡᴀʀɴɪɴɢ!** ⚠️

────═◈═─ ✧◈✧ ─═◈═────
  👤 {user_mention}     
  📊 ᴡᴀʀɴ: {count}/{max}
  📝 ʀᴇᴀsᴏɴ: {reason}  
✦•····················•✦

💀 **ɴᴇxᴛ ᴡᴀʀɴ = ᴀᴄᴛɪᴏɴ!**
"""
    
    MUTE = """
🔇 **ᴍᴜᴛᴇᴅ!** 🔇

────═◈═─ ✧◈✧ ─═◈═────
  👤 {user_mention}     
  ⏱️ {duration}        
  📝 ʀᴇᴀsᴏɴ: {reason}  
✦•····················•✦

🤫 sʜʜʜ... ʙᴇ ǫᴜɪᴇᴛ!
"""
    
    UNMUTE = """
🔊 **ᴜɴᴍᴜᴛᴇᴅ!** 🔊

────═◈═─ ✧◈✧ ─═◈═────
  👤 {user_mention}     
  ✅ ɴᴏᴡ ᴄᴀɴ sᴘᴇᴀᴋ  
✦•····················•✦

🗣️ sᴘᴇᴀᴋ ғʀᴇᴇʟʏ ɴᴏᴡ!
"""
    
    KICK = """
👢 **ᴋɪᴄᴋᴇᴅ!** 👢

────═◈═─ ✧◈✧ ─═◈═────
  👤 {user_mention}     
  📝 ʀᴇᴀsᴏɴ: {reason}  
✦•····················•✦

🚫 ɢᴏᴏᴅʀɪᴅᴅᴀɴᴄᴇ!
"""
    
    BAN = """
🚫 **ʙᴀɴɴᴇᴅ!** 🚫

────═◈═─ ✧◈✧ ─═◈═────
  👤 {user_mention}     
  📝 ʀᴇᴀsᴏɴ: {reason}  
✦•····················•✦

💀 ғᴏʀᴇᴠᴇʀ ɢᴏɴᴇ!
"""
    
    UNBAN = """
✅ **ᴜɴʙᴀɴɴᴇᴅ!** ✅

────═◈═─ ✧◈✧ ─═◈═────
  👤 {user_mention}     
  🎉 ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ!  
✦•····················•✦

🌟 sᴇᴄᴏɴᴅ ᴄʜᴀɴᴄᴇ!
"""

    PREMIUM_START = """
⚡ **ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs** ⚡

────═◈═─ ✧◈✧ ─═◈═────
  💎 ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ            
  🎯 ɴᴀᴍᴇ: {user_name}         
  ✨ sᴛᴀᴛᴜs: ᴀᴄᴛɪᴠᴇ          
✦•····················•✦

🚀 **ᴜɴʟᴏᴄᴋᴇᴅ ғᴇᴀᴛᴜʀᴇs:**
╰┈➤ ᴀɴᴛɪ-ᴄʀᴀsʜ
╰┈➤ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-sᴘᴀᴍ
╰┈➤ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ɢɪғ
╰┈➤ ᴘʀɪᴠᴀᴛᴇ ʟᴏɢs
╰┈➤ 24/7 sᴜᴘᴘᴏʀᴛ

🔥 ᴘᴏᴡᴇʀᴇᴅ ʙʏ {bot_name}
"""
