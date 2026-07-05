import pymongo
from datetime import datetime
from config import Config

class Database:
    def __init__(self):
        self.client = pymongo.MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        
        # Collections
        self.users = self.db.users
        self.groups = self.db.groups
        self.warnings = self.db.warnings
        self.mutes = self.db.mutes
        self.premium = self.db.premium
        self.user_history = self.db.user_history
        self.filters = self.db.filters
        self.settings = self.db.settings
        self.rules = self.db.rules
        self.approved = self.db.approved
        
        # Create indexes
        self.users.create_index("user_id", unique=True)
        self.groups.create_index("chat_id", unique=True)
        self.user_history.create_index([("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])
    
    # User Methods
    async def add_user(self, user_id, username, first_name):
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "first_name": first_name, "last_seen": datetime.now()}},
            upsert=True
        )
    
    async def get_user_stats(self, user_id):
        user = self.users.find_one({"user_id": user_id})
        return user if user else {"messages": 0, "groups": 0}
    
    async def increment_user_messages(self, user_id, chat_id):
        self.users.update_one(
            {"user_id": user_id},
            {"$inc": {"messages": 1}},
            upsert=True
        )
        # Also track groups
        self.groups.update_one(
            {"chat_id": chat_id},
            {"$addToSet": {"members": user_id}},
            upsert=True
        )
    
    async def get_user_message_count(self, user_id):
        user = self.users.find_one({"user_id": user_id})
        return user.get("messages", 0) if user else 0
    
    # User History Methods
    async def add_user_history(self, user_id, data):
        self.user_history.insert_one({
            "user_id": user_id,
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "username": data.get("username"),
            "timestamp": datetime.now().isoformat()
        })
    
    async def get_user_history(self, user_id):
        history = list(self.user_history.find({"user_id": user_id}).sort("timestamp", pymongo.DESCENDING))
        return history
    
    # Group Settings Methods
    async def get_settings(self, chat_id):
        settings = self.settings.find_one({"chat_id": chat_id})
        if not settings:
            settings = {
                "chat_id": chat_id,
                "welcome": True,
                "goodbye": True,
                "antispam": True,
                "antilink": False,
                "anti18": True,
                "warn_limit": 3,
                "admins": []
            }
            self.settings.insert_one(settings)
        return settings
    
    async def update_settings(self, chat_id, key, value):
        self.settings.update_one(
            {"chat_id": chat_id},
            {"$set": {key: value}},
            upsert=True
        )
    
    # Warning Methods
    async def add_warning(self, user_id, chat_id, reason, admin_id):
        self.warnings.insert_one({
            "user_id": user_id,
            "chat_id": chat_id,
            "reason": reason,
            "admin_id": admin_id,
            "timestamp": datetime.now()
        })
    
    async def get_warnings(self, user_id, chat_id):
        return list(self.warnings.find({"user_id": user_id, "chat_id": chat_id}))
    
    async def clear_warnings(self, user_id, chat_id):
        self.warnings.delete_many({"user_id": user_id, "chat_id": chat_id})
    
    # Mute Methods
    async def add_mute(self, user_id, chat_id, duration, reason, admin_id):
        self.mutes.insert_one({
            "user_id": user_id,
            "chat_id": chat_id,
            "duration": duration,
            "reason": reason,
            "admin_id": admin_id,
            "timestamp": datetime.now(),
            "expires": datetime.now() + timedelta(seconds=duration)
        })
    
    async def remove_mute(self, user_id, chat_id):
        self.mutes.delete_many({"user_id": user_id, "chat_id": chat_id})
    
    # Filter Methods
    async def add_filter(self, chat_id, keyword, reply_text):
        self.filters.update_one(
            {"chat_id": chat_id, "keyword": keyword},
            {"$set": {"reply_text": reply_text}},
            upsert=True
        )
    
    async def remove_filter(self, chat_id, keyword):
        self.filters.delete_one({"chat_id": chat_id, "keyword": keyword})
    
    async def get_filters(self, chat_id):
        return list(self.filters.find({"chat_id": chat_id}))
    
    # Rules Methods
    async def set_rules(self, chat_id, rules):
        self.rules.update_one(
            {"chat_id": chat_id},
            {"$set": {"rules": rules}},
            upsert=True
        )
    
    async def get_rules(self, chat_id):
        rule = self.rules.find_one({"chat_id": chat_id})
        return rule.get("rules") if rule else None
    
    # Approve Methods
    async def approve_user(self, user_id, chat_id):
        self.approved.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {"$set": {"approved": True}},
            upsert=True
        )
    
    async def unapprove_user(self, user_id, chat_id):
        self.approved.delete_one({"user_id": user_id, "chat_id": chat_id})
    
    async def is_approved(self, user_id, chat_id):
        return bool(self.approved.find_one({"user_id": user_id, "chat_id": chat_id}))
    
    # Premium Methods
    async def add_premium(self, user_id):
        self.premium.update_one(
            {"user_id": user_id},
            {"$set": {"premium": True, "added": datetime.now()}},
            upsert=True
        )
    
    async def remove_premium(self, user_id):
        self.premium.delete_one({"user_id": user_id})
