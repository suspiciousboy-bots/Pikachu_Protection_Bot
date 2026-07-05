import os

class Config:
    # Bot Configuration
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    BOT_NAME = "Pikachu Protection Bot"
    BOT_USERNAME = "@YourBotUsername"
    
    # Owner Configuration
    OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
    OWNER_NAME = "Your Name"
    OWNER_USERNAME = "@YourUsername"
    
    # Premium Users (List of user IDs)
    PREMIUM_USERS = [123456789, 987654321]
    
    # Moderation Settings
    MAX_WARNINGS = 3
    MUTE_DURATION = 300  # Seconds
    
    # Log Channel
    LOG_CHANNEL = -1003424504397
    
    # Database
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = "pikachu_bot"
