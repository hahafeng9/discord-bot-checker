import requests
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# 配置信息
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
WEBSITE_URL = "https://billing.darkless.cloud/products/discord/256mb"
SEARCH_TEXT = "Free Discord Bot Hosting"
SCREENSHOT_PATH = "screenshot.png"

def take_screenshot():
    """使用Selenium截图网页"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 后台运行
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=options)
        driver.get(WEBSITE_URL)
        
        # 等待页面加载
        time.sleep(3)
        
        # 截图
        driver.save_screenshot(SCREENSHOT_PATH)
        driver.quit()
        
        print("✅ 截图成功")
        return True
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return False

def check_website():
    """检查网站内容"""
    try:
        response = requests.get(WEBSITE_URL, timeout=10)
        response.encoding = 'utf-8'
        
        if SEARCH_TEXT in response.text:
            return True, "✅ 找到内容：Free Discord Bot Hosting"
        else:
            return False, "❌ 未找到内容"
    except RequestException as e:
        return False, f"❌ 网络错误: {e}"

def send_telegram_photo(message):
    """发送截图到Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        with open(SCREENSHOT_PATH, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 截图已发送到Telegram")
            return True
        else:
            print(f"❌ 发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def send_telegram_message(message):
    """发送文字消息到Telegram（备用）"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def main():
    print(f"⏰ 开始检查: {WEBSITE_URL}")
    
    # 1. 截图
    if not take_screenshot():
        print("⚠️ 截图失败，仍尝试发送消息")
        send_telegram_message("⚠️ 网站检查失败，无法截图")
        return
    
    # 2. 检查内容
    found, status_msg = check_website()
    
    # 3. 构建消息
    if found:
        message = f"🎉 <b>发现内容！</b>\n\n🔗 网址: {WEBSITE_URL}\n\n📝 状态: {status_msg}\n\n⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        message = f"🔍 <b>网站检查完毕</b>\n\n🔗 网址: {WEBSITE_URL}\n\n📝 状态: {status_msg}\n\n⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    # 4. 发送截图
    send_telegram_photo(message)
    
    # 清理
    if os.path.exists(SCREENSHOT_PATH):
        os.remove(SCREENSHOT_PATH)

if __name__ == "__main__":
    main()
