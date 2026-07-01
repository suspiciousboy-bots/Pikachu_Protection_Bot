from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    
    @staticmethod
    def main_menu(is_premium=False):
        """Main menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 sᴛᴀᴛs", callback_data="stats"),
                InlineKeyboardButton("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📖 ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about")
            ]
        ]
        
        if is_premium:
            keyboard.append([
                InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu():
        """Settings menu keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("👋 ᴡᴇʟᴄᴏᴍᴇ", callback_data="set_welcome"),
                InlineKeyboardButton("👋 ɢᴏᴏᴅʙʏᴇ", callback_data="set_goodbye")
            ],
            [
                InlineKeyboardButton("🛡️ ᴀɴᴛɪ-sᴘᴀᴍ", callback_data="set_antispam"),
                InlineKeyboardButton("🔗 ᴀɴᴛɪ-ʟɪɴᴋ", callback_data="set_antilink")
            ],
            [
                InlineKeyboardButton("⚠️ ᴡᴀʀɴ ʟɪᴍɪᴛ", callback_data="set_warnlimit"),
                InlineKeyboardButton("🔇 ᴍᴜᴛᴇ ᴛɪᴍᴇ", callback_data="set_mutetime")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def toggle_keyboard(setting_name, current_value):
        """Toggle on/off keyboard for settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if current_value else '❌'} ᴛᴏɢɢʟᴇ",
                    callback_data=f"toggle_{setting_name}"
                )
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def premium_keyboard():
        """Premium features keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("💰 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ", callback_data="buy_premium"),
                InlineKeyboardButton("💎 ᴄʜᴇᴄᴋ sᴛᴀᴛᴜs", callback_data="check_premium")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_main")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def warning_limit_keyboard():
        """Warning limit settings keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("2", callback_data="set_warnlimit_2"),
                InlineKeyboardButton("3", callback_data="set_warnlimit_3"),
                InlineKeyboardButton("5", callback_data="set_warnlimit_5")
            ],
            [
                InlineKeyboardButton("10", callback_data="set_warnlimit_10"),
                InlineKeyboardButton("∞", callback_data="set_warnlimit_0")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def mute_duration_keyboard():
        """Mute duration settings keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("5ᴍ", callback_data="set_mutetime_300"),
                InlineKeyboardButton("10ᴍ", callback_data="set_mutetime_600"),
                InlineKeyboardButton("30ᴍ", callback_data="set_mutetime_1800")
            ],
            [
                InlineKeyboardButton("1ʜ", callback_data="set_mutetime_3600"),
                InlineKeyboardButton("6ʜ", callback_data="set_mutetime_21600"),
                InlineKeyboardButton("12ʜ", callback_data="set_mutetime_43200")
            ],
            [
                InlineKeyboardButton("1ᴅ", callback_data="set_mutetime_86400"),
                InlineKeyboardButton("7ᴅ", callback_data="set_mutetime_604800")
            ],
            [
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_settings")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
