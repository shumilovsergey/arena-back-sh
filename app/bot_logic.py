"""
Telegram Bot Logic
Separate from WebApp functionality - handles chat bot interactions
"""

import json
import requests
from typing import Optional, Dict, Any
from .telegram_utils import Message, parse_telegram_update
from .database import UserManager
from .constants import TELEGRAM_API_BASE, FRONT_URL, SHUMILOV_WEBSITE


class TelegramBot:
    """Telegram Bot API wrapper and message handler"""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.api_base = TELEGRAM_API_BASE

    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML",
                     reply_markup: Optional[Dict] = None) -> bool:
        """Send text message to chat"""
        url = f"{self.api_base}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                # Get message_id from response to track it
                result = response.json()
                if result.get('ok') and 'result' in result:
                    message_id = result['result'].get('message_id')
                    if message_id:
                        return message_id  # Return message_id instead of True
                return True
            return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def send_message_clean(self, chat_id: int, text: str, parse_mode: str = "HTML",
                          reply_markup: Optional[Dict] = None) -> bool:
        """Send message and clean previous bot message"""
        # Delete previous bot message
        last_message_id = UserManager.get_last_bot_message_id(chat_id)
        if last_message_id:
            self.delete_message(chat_id, last_message_id)

        # Send new message
        new_message_id = self.send_message(chat_id, text, parse_mode, reply_markup)

        # Store new message ID if send was successful
        if new_message_id and isinstance(new_message_id, int):
            UserManager.set_last_bot_message_id(chat_id, new_message_id)
            return True
        elif new_message_id:  # If it returned True (old behavior)
            return True

        return False

    def send_photo(self, chat_id: int, photo: str, caption: str = "",
                   reply_markup: Optional[Dict] = None) -> bool:
        """Send photo to chat"""
        url = f"{self.api_base}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                # Get message_id from response to track it
                result = response.json()
                if result.get('ok') and 'result' in result:
                    message_id = result['result'].get('message_id')
                    if message_id:
                        return message_id  # Return message_id instead of True
                return True
            return False
        except Exception as e:
            print(f"Error sending photo: {e}")
            return False

    def send_photo_clean(self, chat_id: int, photo: str, caption: str = "",
                        reply_markup: Optional[Dict] = None) -> bool:
        """Send photo and clean previous bot message"""
        # Delete previous bot message
        last_message_id = UserManager.get_last_bot_message_id(chat_id)
        if last_message_id:
            self.delete_message(chat_id, last_message_id)

        # Send new photo
        new_message_id = self.send_photo(chat_id, photo, caption, reply_markup)

        # Store new message ID if send was successful
        if new_message_id and isinstance(new_message_id, int):
            UserManager.set_last_bot_message_id(chat_id, new_message_id)
            return True
        elif new_message_id:  # If it returned True (old behavior)
            return True

        return False

    def edit_message_text(self, chat_id: int, message_id: int, text: str,
                          parse_mode: str = "HTML", reply_markup: Optional[Dict] = None) -> bool:
        """Edit existing message text"""
        url = f"{self.api_base}/editMessageText"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error editing message: {e}")
            return False

    def answer_callback_query(self, callback_query_id: str, text: str = "",
                              show_alert: bool = False) -> bool:
        """Answer callback query"""
        url = f"{self.api_base}/answerCallbackQuery"
        payload = {
            "callback_query_id": callback_query_id,
            "text": text,
            "show_alert": show_alert
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error answering callback query: {e}")
            return False

    def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Delete a message"""
        url = f"{self.api_base}/deleteMessage"
        payload = {
            "chat_id": chat_id,
            "message_id": message_id
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error deleting message: {e}")
            return False


class BotMessageHandler:
    """Handle different types of bot messages and commands"""

    def __init__(self, bot: TelegramBot):
        self.bot = bot

    def handle_update(self, update: Dict[str, Any]) -> bool:
        """Main update handler - routes to appropriate handlers"""
        try:
            message = parse_telegram_update(update)

            if not message.user_id or not message.chat_id:
                return False

            # Handle different update types
            if message.callback_data:
                return self.handle_callback_query(message, update.get('callback_query', {}))
            elif message.text:
                return self.handle_text_message(message)
            elif message.has_media():
                return self.handle_media_message(message)
            else:
                return self.handle_unknown_message(message)

        except Exception as e:
            print(f"Error handling update: {e}")
            return False

    def handle_text_message(self, message: Message) -> bool:
        """Handle text messages and commands"""
        text = message.text.strip()

        # Handle commands
        if text.startswith('/'):
            return self.handle_command(message, text)

        # Handle regular text
        return self.handle_regular_text(message, text)

    def handle_command(self, message: Message, command: str) -> bool:
        """Handle bot commands"""
        command_lower = command.lower()

        if command_lower in ['/start', '/help']:
            return self.handle_start_command(message)
        else:
            return self.handle_unknown_command(message, command)

    def handle_start_command(self, message: Message) -> bool:
        """Handle /start command"""
        user_name = message.get_full_name()

        # Always check if user exists in Redis, create if not
        user = UserManager.get_user(message.user_id)
        if not user:
            print(f"Creating new user from bot /start: {message.user_id}")
            user = UserManager.create_user(
                telegram_id=message.user_id,
                first_name=message.first_name or '',
                last_name=message.last_name or '',
                username=message.username or '',
                language_code='en'  # Default, could be extracted from update
            )
        else:
            print(f"Existing user started bot: {message.user_id}")

        # Clear any previous bot message tracking when user restarts
        UserManager.clear_last_bot_message_id(message.user_id)

        welcome_text = f"""
👋 Hello, <b>{user_name}</b>!

Welcome to our Telegram App Template!

        """.strip()

        # Create inline keyboard with web app button
        keyboard = {
            "inline_keyboard": [
                [{"text": "🚀 Open Web App", "web_app": {"url": FRONT_URL}}],
                [{"text": "👨‍💻 About me", "url": SHUMILOV_WEBSITE}]
            ]
        }

        return self.bot.send_message_clean(message.chat_id, welcome_text, reply_markup=keyboard)


    def handle_unknown_command(self, message: Message, command: str) -> bool:
        """Handle unknown commands"""
        text = f"""
❓ Unknown command: <code>{command}</code>

Available commands:
/start - Main menu
/help - Show help
        """.strip()

        return self.bot.send_message_clean(message.chat_id, text)

    def handle_regular_text(self, message: Message, text: str) -> bool:
        """Handle regular text messages"""
        text_lower = text.lower().strip()

        # IMPORTANT: Never delete /start command!
        if text_lower == '/start':
            print(f"Received /start command from user {message.user_id} - NOT deleting")
            # Don't delete /start, let it be handled by command handler
            return True

        # Simple if/elif/else dialog script
        if text_lower in ['hi', 'hello', 'hey', 'привет']:
            response = f"Hello {message.get_full_name()}! 👋\n\nUse /start to see available options."
            return self.bot.send_message_clean(message.chat_id, response)

        elif text_lower in ['help', 'помощь']:
            return self.handle_start_command(message)

        elif text_lower in ['thanks', 'thank you', 'спасибо']:
            response = "You're welcome! 😊"
            return self.bot.send_message_clean(message.chat_id, response)

        # Add more elif conditions here for your specific dialog script
        # elif text_lower == 'some_keyword':
        #     response = "Your response here"
        #     return self.bot.send_message(message.chat_id, response)

        else:
            # Message doesn't match any dialog script - delete it
            print(f"Deleting unhandled message from user {message.user_id}: '{text}'")
            self.bot.delete_message(message.chat_id, message.message_id)
            return True

    # def handle_callback_query(self, message: Message, callback_query: Dict) -> bool:
    #     """Handle callback button presses"""
    #     callback_data = message.callback_data
    #     callback_query_id = callback_query.get('id')

    #     # Answer callback query first
    #     self.bot.answer_callback_query(callback_query_id)

    #     # Handle different callback data
    #     if callback_data == "start":
    #         return self.handle_start_command(message)
    #     elif callback_data == "profile":
    #         return self.handle_profile_command(message)
    #     elif callback_data == "settings":
    #         return self.handle_settings_command(message)
    #     elif callback_data == "settings_notifications":
    #         return self.handle_settings_notifications(message)
    #     elif callback_data == "settings_language":
    #         return self.handle_settings_language(message)
    #     else:
    #         return self.handle_unknown_callback(message, callback_data)


    def handle_unknown_callback(self, message: Message, callback_data: str) -> bool:
        """Handle unknown callback data"""
        text = f"❓ Unknown action: {callback_data}"
        return self.bot.send_message_clean(message.chat_id, text)

    def handle_media_message(self, message: Message) -> bool:
        """Handle media messages (photos, videos, etc.)"""
        # Simple media handling - you can add specific logic here if needed

        if message.photo:
            # Handle photo - you can add specific photo logic here
            # For now, just delete unhandled photos
            print(f"Deleting unhandled photo from user {message.user_id}")
            self.bot.delete_message(message.chat_id, message.message_id)
            return True

        elif message.video:
            # Handle video - you can add specific video logic here
            print(f"Deleting unhandled video from user {message.user_id}")
            self.bot.delete_message(message.chat_id, message.message_id)
            return True

        elif message.voice:
            # Handle voice - you can add specific voice logic here
            print(f"Deleting unhandled voice from user {message.user_id}")
            self.bot.delete_message(message.chat_id, message.message_id)
            return True

        elif message.document:
            # Handle document - you can add specific document logic here
            print(f"Deleting unhandled document from user {message.user_id}")
            self.bot.delete_message(message.chat_id, message.message_id)
            return True

        else:
            # Unknown media type
            print(f"Deleting unknown media from user {message.user_id}")
            self.bot.delete_message(message.chat_id, message.message_id)
            return True

    def handle_unknown_message(self, message: Message) -> bool:
        """Handle unknown message types"""
        # Delete unknown message types as well
        print(f"Deleting unknown message type from user {message.user_id}")
        self.bot.delete_message(message.chat_id, message.message_id)
        return True