import requests
import os
from requests.exceptions import RequestException

# 从环境变量读取敏感信息
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBSITE_URL = "https://billing.darkless.cloud/products/discord/256mb"
SEARCH_TEXT = "Free Discord Bot Hosting"

def check_website_and_notify():
    try:
        response = requests.get(WEBSITE_URL, timeout=10)
        response.encoding = 'utf-8'
        
        if SEARCH_TEXT in response.text:
            send_telegram_message(f"🎉 发现内容！\n网站: {WEBSITE_URL}\n包含: {SEARCH_TEXT}")
            print("✅ 找到内容，已发送消息")
            return True
        else:
            print("❌ 未找到指定内容")
            return False
            
    except RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except RequestException as e:
        print(f"❌ 发送错误: {e}")
        return False

if __name__ == "__main__":
    check_website_and_notify()
