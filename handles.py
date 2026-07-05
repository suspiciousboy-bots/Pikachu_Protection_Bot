"""
Database Module for Pikachu Protection Bot
Handles all database operations using MongoDB
"""

import pymongo
from datetime import datetime, timedelta
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Initialize database connection and collections"""
        try:
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
            self.user_roles = self.db.user_roles
            self.messages = self.db.messages
            
            # Create indexes for better performance
            self.users.create_index("user_id", unique=True)
            self.groups.create_index("chat_id", unique=True)
            self.user_history.create_index([("user_id", pymongo.ASCENDING), ("timestamp", pymongo.DESCENDING)])
            self.warnings.create_index([("user_id", pymongo.ASCENDING), ("chat_id", pymongo.ASCENDING)])
            self.mutes.create_index([("user_id", pymongo.ASCENDING), ("chat_id", pymongo.ASCENDING)])
            self.user_roles.create_index([("user_id", pymongo.ASCENDING), ("chat_id", pymongo.ASCENDING)])
            self.filters.create_index([("chat_id", pymongo.ASCENDING), ("keyword", pymongo.ASCENDING)], unique=True)
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    # ────═◈═─ USER METHODS ─═◈═────
    
    async def add_user(self, user_id, username, first_name):
        """Add or update user in database"""
        try:
            self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "first_name": first_name,
                        "last_seen": datetime.now()
                    },
                    "$inc": {"groups": 1}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False

    async def get_user_stats(self, user_id):
        """Get user statistics"""
        try:
            user = self.users.find_one({"user_id": user_id})
            if user:
                return {
                    "messages": user.get("messages", 0),
                    "groups": user.get("groups", 0),
                    "warns": user.get("warns", 0),
                    "last_seen": user.get("last_seen")
                }
            return {"messages": 0, "groups": 0, "warns": 0}
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {"messages": 0, "groups": 0, "warns": 0}

    async def increment_user_messages(self, user_id, chat_id):
        """Increment user's message count and track group"""
        try:
            # Increment user messages
            self.users.update_one(
                {"user_id": user_id},
                {"$inc": {"messages": 1}},
                upsert=True
            )
            
            # Track group membership
            self.groups.update_one(
                {"chat_id": chat_id},
                {"$addToSet": {"members": user_id}},
                upsert=True
            )
            
            # Track message in group
            self.messages.insert_one({
                "user_id": user_id,
                "chat_id": chat_id,
                "timestamp": datetime.now()
            })
            return True
        except Exception as e:
            logger.error(f"Error incrementing messages for {user_id}: {e}")
            return False

    async def get_user_message_count(self, user_id):
        """Get total messages sent by user"""
        try:
            user = self.users.find_one({"user_id": user_id})
            return user.get("messages", 0) if user else 0
        except Exception as e:
            logger.error(f"Error getting message count for {user_id}: {e}")
            return 0

    # ────═◈═─ USER HISTORY METHODS ─═◈═────
    
    async def add_user_history(self, user_id, data):
        """Add user history entry"""
        try:
            entry = {
                "user_id": user_id,
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "username": data.get("username", ""),
                "timestamp": datetime.now().isoformat()
            }
            self.user_history.insert_one(entry)
            return True
        except Exception as e:
            logger.error(f"Error adding user history for {user_id}: {e}")
            return False

    async def get_user_history(self, user_id):
        """Get user's full history"""
        try:
            history = list(self.user_history.find(
                {"user_id": user_id}
            ).sort("timestamp", pymongo.DESCENDING))
            return history
        except Exception as e:
            logger.error(f"Error getting user history for {user_id}: {e}")
            return []

    async def get_user_history_count(self, user_id):
        """Get count of user history entries"""
        try:
            return self.user_history.count_documents({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting history count for {user_id}: {e}")
            return 0

    # ────═◈═─ USER ROLE METHODS ─═◈═────
    
    async def set_user_role(self, user_id, chat_id, role):
        """Set user role in a group"""
        try:
            self.user_roles.update_one(
                {"user_id": user_id, "chat_id": chat_id},
                {
                    "$set": {
                        "role": role,
                        "updated": datetime.now()
                    }
                },
                upsert=True
            )
            logger.info(f"Role {role} set for user {user_id} in chat {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting role for {user_id}: {e}")
            return False

    async def remove_user_role(self, user_id, chat_id):
        """Remove user role"""
        try:
            result = self.user_roles.delete_one({"user_id": user_id, "chat_id": chat_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing role for {user_id}: {e}")
            return False

    async def get_user_role(self, user_id, chat_id):
        """Get user role in a group"""
        try:
            role_data = self.user_roles.find_one({"user_id": user_id, "chat_id": chat_id})
            if role_data:
                return role_data.get("role", "Member")
            return "Member"
        except Exception as e:
            logger.error(f"Error getting role for {user_id}: {e}")
            return "Member"

    async def get_all_staff(self, chat_id):
        """Get all staff members for a group"""
        try:
            staff_roles = ['Founder', 'Co-Founder', 'Admin', 'Moderator', 'Muter', 'Chat Cleaner', 'Helper', 'Free']
            staff = list(self.user_roles.find(
                {"chat_id": chat_id, "role": {"$in": staff_roles}}
            ))
            
            for member in staff:
                user = self.users.find_one({"user_id": member["user_id"]})
                if user:
                    member["first_name"] = user.get("first_name", "Unknown")
                    member["username"] = user.get("username", "")
            
            return staff
        except Exception as e:
            logger.error(f"Error getting staff for {chat_id}: {e}")
            return []

    # ────═◈═─ GROUP SETTINGS METHODS ─═◈═────
    
    async def get_settings(self, chat_id):
        """Get group settings"""
        try:
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
        except Exception as e:
            logger.error(f"Error getting settings for {chat_id}: {e}")
            return {
                "chat_id": chat_id,
                "welcome": True,
                "goodbye": True,
                "antispam": True,
                "antilink": False,
                "anti18": True,
                "warn_limit": 3,
                "admins": []
            }

    async def update_settings(self, chat_id, key, value):
        """Update group settings"""
        try:
            self.settings.update_one(
                {"chat_id": chat_id},
                {"$set": {key: value}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating settings for {chat_id}: {e}")
            return False

    # ────═◈═─ WARNING METHODS ─═◈═────
    
    async def add_warning(self, user_id, chat_id, reason, admin_id):
        """Add a warning to user"""
        try:
            self.warnings.insert_one({
                "user_id": user_id,
                "chat_id": chat_id,
                "reason": reason,
                "admin_id": admin_id,
                "timestamp": datetime.now()
            })
            
            # Update user's warn count
            self.users.update_one(
                {"user_id": user_id},
                {"$inc": {"warns": 1}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding warning for {user_id}: {e}")
            return False

    async def get_warnings(self, user_id, chat_id):
        """Get user's warnings"""
        try:
            warnings = list(self.warnings.find(
                {"user_id": user_id, "chat_id": chat_id}
            ).sort("timestamp", pymongo.DESCENDING))
            return warnings
        except Exception as e:
            logger.error(f"Error getting warnings for {user_id}: {e}")
            return []

    async def clear_warnings(self, user_id, chat_id):
        """Clear all warnings for user"""
        try:
            result = self.warnings.delete_many({"user_id": user_id, "chat_id": chat_id})
            self.users.update_one(
                {"user_id": user_id},
                {"$set": {"warns": 0}},
                upsert=True
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error clearing warnings for {user_id}: {e}")
            return False

    async def get_warning_count(self, user_id, chat_id):
        """Get number of warnings for user"""
        try:
            return self.warnings.count_documents({"user_id": user_id, "chat_id": chat_id})
        except Exception as e:
            logger.error(f"Error getting warning count for {user_id}: {e}")
            return 0

    # ────═◈═─ MUTE METHODS ─═◈═────
    
    async def add_mute(self, user_id, chat_id, duration, reason, admin_id):
        """Mute a user"""
        try:
            expires = datetime.now() + timedelta(seconds=duration)
            self.mutes.update_one(
                {"user_id": user_id, "chat_id": chat_id},
                {
                    "$set": {
                        "duration": duration,
                        "reason": reason,
                        "admin_id": admin_id,
                        "timestamp": datetime.now(),
                        "expires": expires
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error muting user {user_id}: {e}")
            return False

    async def remove_mute(self, user_id, chat_id):
        """Unmute a user"""
        try:
            result = self.mutes.delete_one({"user_id": user_id, "chat_id": chat_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing mute for {user_id}: {e}")
            return False

    async def is_muted(self, user_id, chat_id):
        """Check if user is muted"""
        try:
            mute = self.mutes.find_one({"user_id": user_id, "chat_id": chat_id})
            if not mute:
                return False
            expires = mute.get("expires")
            if expires and datetime.now() > expires:
                await self.remove_mute(user_id, chat_id)
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking mute for {user_id}: {e}")
            return False

    # ────═◈═─ FILTER METHODS ─═◈═────
    
    async def add_filter(self, chat_id, keyword, reply_text):
        """Add a filter to group"""
        try:
            self.filters.update_one(
                {"chat_id": chat_id, "keyword": keyword.lower()},
                {"$set": {"reply_text": reply_text}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding filter for {chat_id}: {e}")
            return False

    async def remove_filter(self, chat_id, keyword):
        """Remove a filter from group"""
        try:
            result = self.filters.delete_one({"chat_id": chat_id, "keyword": keyword.lower()})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing filter for {chat_id}: {e}")
            return False

    async def get_filters(self, chat_id):
        """Get all filters for group"""
        try:
            filters = list(self.filters.find({"chat_id": chat_id}))
            return filters
        except Exception as e:
            logger.error(f"Error getting filters for {chat_id}: {e}")
            return []

    # ────═◈═─ RULES METHODS ─═◈═────
    
    async def set_rules(self, chat_id, rules):
        """Set group rules"""
        try:
            self.rules.update_one(
                {"chat_id": chat_id},
                {"$set": {"rules": rules, "updated": datetime.now()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting rules for {chat_id}: {e}")
            return False

    async def get_rules(self, chat_id):
        """Get group rules"""
        try:
            rule = self.rules.find_one({"chat_id": chat_id})
            return rule.get("rules") if rule else None
        except Exception as e:
            logger.error(f"Error getting rules for {chat_id}: {e}")
            return None

    # ────═◈═─ APPROVE METHODS ─═◈═────
    
    async def approve_user(self, user_id, chat_id):
        """Approve user to send links"""
        try:
            self.approved.update_one(
                {"user_id": user_id, "chat_id": chat_id},
                {"$set": {"approved": True, "timestamp": datetime.now()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error approving user {user_id}: {e}")
            return False

    async def unapprove_user(self, user_id, chat_id):
        """Unapprove user from sending links"""
        try:
            result = self.approved.delete_one({"user_id": user_id, "chat_id": chat_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error unapproving user {user_id}: {e}")
            return False

    async def is_approved(self, user_id, chat_id):
        """Check if user is approved"""
        try:
            return bool(self.approved.find_one({"user_id": user_id, "chat_id": chat_id}))
        except Exception as e:
            logger.error(f"Error checking approval for {user_id}: {e}")
            return False

    # ────═◈═─ PREMIUM METHODS (ADDED) ─═◈═────
    
    async def add_premium(self, user_id):
        """Add premium user"""
        try:
            self.premium.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "premium": True,
                        "added": datetime.now(),
                        "expires": datetime.now() + timedelta(days=30)
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding premium for {user_id}: {e}")
            return False

    async def remove_premium(self, user_id):
        """Remove premium user"""
        try:
            result = self.premium.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error removing premium for {user_id}: {e}")
            return False

    async def check_premium(self, user_id):
        """Check if user is premium"""
        try:
            premium = self.premium.find_one({"user_id": user_id})
            if not premium:
                return False
            expires = premium.get("expires")
            if expires and datetime.now() > expires:
                await self.remove_premium(user_id)
                return False
            return premium.get("premium", False)
        except Exception as e:
            logger.error(f"Error checking premium for {user_id}: {e}")
            return False

    async def is_premium(self, user_id):
        """Check if user is premium (alias for check_premium)"""
        return await self.check_premium(user_id)

    # ────═◈═─ GROUP STATS METHODS ─═◈═────
    
    async def get_group_stats(self, chat_id):
        """Get group statistics"""
        try:
            group = self.groups.find_one({"chat_id": chat_id})
            if not group:
                return {
                    "members": 0,
                    "messages": 0,
                    "active_users": 0
                }
            week_ago = datetime.now() - timedelta(days=7)
            active_users = self.messages.distinct(
                "user_id",
                {"chat_id": chat_id, "timestamp": {"$gte": week_ago}}
            )
            return {
                "members": len(group.get("members", [])),
                "messages": group.get("messages", 0),
                "active_users": len(active_users)
            }
        except Exception as e:
            logger.error(f"Error getting group stats for {chat_id}: {e}")
            return {"members": 0, "messages": 0, "active_users": 0}

    # ────═◈═─ CLEANUP METHODS ─═◈═────
    
    async def cleanup_expired_mutes(self):
        """Remove expired mutes"""
        try:
            expired = self.mutes.find({"expires": {"$lt": datetime.now()}})
            for mute in expired:
                await self.remove_mute(mute["user_id"], mute["chat_id"])
            return True
        except Exception as e:
            logger.error(f"Error cleaning up expired mutes: {e}")
            return False

    async def cleanup_old_history(self, days=30):
        """Remove old history entries"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            result = self.user_history.delete_many({"timestamp": {"$lt": cutoff.isoformat()}})
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old history: {e}")
            return 0

    # ────═◈═─ BOT STATS METHODS ─═◈═────
    
    async def get_bot_stats(self):
        """Get bot statistics"""
        try:
            return {
                "users": self.users.count_documents({}),
                "groups": self.groups.count_documents({}),
                "warnings": self.warnings.count_documents({}),
                "mutes": self.mutes.count_documents({}),
                "premium": self.premium.count_documents({}),
                "history": self.user_history.count_documents({}),
                "filters": self.filters.count_documents({}),
                "messages": self.messages.count_documents({})
            }
        except Exception as e:
            logger.error(f"Error getting bot stats: {e}")
            return {}

    # ────═◈═─ INACTIVE USERS ─═◈═────
    
    async def get_inactive_users(self, chat_id, days=7):
        """Get inactive users in a group"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            active_users = self.messages.distinct(
                "user_id",
                {"chat_id": chat_id, "timestamp": {"$gte": cutoff}}
            )
            group = self.groups.find_one({"chat_id": chat_id})
            if not group:
                return []
            all_users = group.get("members", [])
            inactive = [user for user in all_users if user not in active_users]
            return inactive
        except Exception as e:
            logger.error(f"Error getting inactive users for {chat_id}: {e}")
            return []

    # ────═◈═─ MESSAGE STATS ─═◈═────
    
    async def get_message_stats(self, chat_id, days=7):
        """Get message statistics for a group"""
        try:
            cutoff = datetime.now() - timedelta(days=days)
            pipeline = [
                {"$match": {"chat_id": chat_id, "timestamp": {"$gte": cutoff}}},
                {"$group": {
                    "_id": "$user_id",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            top_users = list(self.messages.aggregate(pipeline))
            total_messages = self.messages.count_documents({
                "chat_id": chat_id,
                "timestamp": {"$gte": cutoff}
            })
            return {
                "total": total_messages,
                "top_users": top_users
            }
        except Exception as e:
            logger.error(f"Error getting message stats for {chat_id}: {e}")
            return {"total": 0, "top_users": []}

    # ────═◈═─ CLOSE CONNECTION ─═◈═────
    
    def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
