# Telegram Service Module - Bot Integration for Harvest Sync
import requests
from django.conf import settings


class TelegramService:
    """Service for sending notifications via Telegram Bot"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, chat_id, message, parse_mode='HTML'):
        """
        Send a text message to a Telegram chat
        """
        try:
            url = f"{self.api_base}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Telegram send error: {str(e)}")
            return {'ok': False, 'error': str(e)}
    
    def send_weather_alert(self, chat_id, alert, language='en'):
        """
        Send a formatted weather alert to a farmer
        """
        message_key = 'message_ml' if language == 'ml' else 'message'
        message_text = alert.get(message_key, alert.get('message', 'Weather Alert'))
        
        # Format with emojis based on alert type
        icon = self._get_alert_icon(alert.get('type'))
        
        formatted_message = f"""
{icon} <b>Harvest Sync Weather Alert</b> {icon}

{message_text}

<i>Stay safe and protect your crops!</i>
        """.strip()
        
        return self.send_message(chat_id, formatted_message)
    
    def send_test_alert(self, chat_id, language='en'):
        """
        Send a test/demo alert
        """
        if language == 'ml':
            message = """
⚡ <b>ഹാർവെസ്റ്റ് സിങ്ക് ടെസ്റ്റ് അലേർട്ട്</b> ⚡

ഇത് ഡെമോ ആവശ്യങ്ങൾക്കുള്ള ഒരു ടെസ്റ്റ് അലേർട്ട് ആണ്.

നിങ്ങളുടെ പ്രദേശത്ത് കനത്ത മഴ പ്രതീക്ഷിക്കുന്നു (75mm).
വിളകൾ സംരക്ഷിക്കുകയും ഡ്രെയിനേജ് ഉറപ്പാക്കുകയും ചെയ്യുക.

<i>സുരക്ഷിതരായിരിക്കുക! 🌾</i>
            """.strip()
        else:
            message = """
⚡ <b>Harvest Sync Test Alert</b> ⚡

This is a test alert for demonstration purposes.

Heavy rainfall expected in your area (75mm).
Protect crops and ensure proper drainage.

<i>Stay safe! 🌾</i>
            """.strip()
        
        return self.send_message(chat_id, message)
    
    def _get_alert_icon(self, alert_type):
        """Get emoji icon for alert type"""
        icons = {
            'heavy_rain': '🌧️',
            'high_temperature': '🌡️',
            'strong_wind': '💨',
            'low_temperature': '❄️',
            'high_uv': '☀️',
            'demo': '⚡'
        }
        return icons.get(alert_type, '⚠️')
    
    def verify_bot(self):
        """Verify bot token is valid"""
        try:
            url = f"{self.api_base}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Bot verification error: {str(e)}")
            return {'ok': False, 'error': str(e)}
    
    def get_updates(self, offset=None):
        """
        Get updates from Telegram (for bot command processing)
        Used by the bot listener command
        """
        try:
            url = f"{self.api_base}/getUpdates"
            params = {'timeout': 30}
            if offset:
                params['offset'] = offset
            
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Get updates error: {str(e)}")
            return {'ok': False, 'error': str(e)}
