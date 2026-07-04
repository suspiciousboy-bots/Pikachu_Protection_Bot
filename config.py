import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ────═◈═─ BOT CONFIGURATION ─═◈═────
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # ────═◈═─ MONGODB ─═◈═────
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = os.getenv("DB_NAME", "pikachu_protection")
    
    # ────═◈═─ OWNER ─═◈═────
    OWNER_ID = int(os.getenv("OWNER_ID", "7790607144"))
    OWNER_NAME = os.getenv("OWNER_NAME", "⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐")
    OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@CrazyyCore")
    
    # ────═◈═─ BOT INFO ─═◈═────
    BOT_NAME = os.getenv("BOT_NAME", "── ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ──")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "@Pikachu_Protection_Robot")
    
    # ────═◈═─ PREMIUM USERS ─═◈═────
    PREMIUM_USERS = [int(id) for id in os.getenv("PREMIUM_USERS", "7790607144").split(",") if id]
    
    # ────═◈═─ PROTECTION SETTINGS ─═◈═────
    MAX_WARNINGS = int(os.getenv("MAX_WARNINGS", "3"))
    MUTE_DURATION = int(os.getenv("MUTE_DURATION", "300"))
    FLOOD_LIMIT = int(os.getenv("FLOOD_LIMIT", "5"))
    LOG_CHANNEL = os.getenv("LOG_CHANNEL", "")
