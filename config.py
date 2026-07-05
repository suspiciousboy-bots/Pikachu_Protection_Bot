import os

class Config:
    # Bot Configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    BOT_NAME = "── ᴘɪᴋᴀᴄʜᴜ ✗ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ ──"
    BOT_USERNAME = "@Pikachu_Protection_Robot"
    
    # Owner Configuration
    OWNER_ID = int(os.environ.get("OWNER_ID", "7790607144"))  # Your ID
    OWNER_NAME = "⏤͟͞ 𝐂𝐑𝐀𝐙𝐘 𝐁𝐎𝐘 ᭄࿐"  # Your name
    OWNER_USERNAME = "@OfficiallyCrazyBoy07"  # Your username
    
    # Premium Users (List of user IDs)
    PREMIUM_USERS = [
        7790607144,  # Your ID
        # Add more premium user IDs here
    ]
    
    # Moderation Settings
    MAX_WARNINGS = 3
    MUTE_DURATION = 300  # Seconds (5 minutes)
    
    # Log Channel (where bot logs will be sent)
    LOG_CHANNEL = -1003424504397
    
    # Database
    MONGO_URI = os.environ.get("MONGO_URI","")
    DB_NAME = "pikachu_bot"
