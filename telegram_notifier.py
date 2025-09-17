import requests
import os

class TelegramNotifier:
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    def send(self, message: str):
        if not self.token or not self.chat_id:
            print("[WARN] Telegram not configured")
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print("[ERROR] Failed to send Telegram message:", e)
