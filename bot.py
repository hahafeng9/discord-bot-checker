import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WEBSITE_URL = "https://billing.darkless.cloud/products/discord/256mb"
SCREENSHOT_PATH = "screenshot.png"

def take_screenshot():
    """Selenium截图网页"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=options)
        driver.get(WEBSITE_URL)
        time.sleep(3)
        driver.save_screenshot(SCREENSHOT_PATH)
        
        # 获取页面文本内容
        page_text = driver.page_source
        driver.quit()
        
        return True, page_text
    except Exception as e:
        print(f"❌ 截图失败: {e}")
        return False, ""

def check_stock_status(page_text):
    """检查库存状态"""
    # 检查是否显示缺货
    out_of_stock_indicators = [
        "out of stock",
        "out of Stock",
        "temporarily blocked",
        "Temporarily blocked"
    ]
    
    is_out_of_stock = any(indicator in page_text for indicator in out_of_stock_indicators)
    
    return not is_out_of_stock  # 返回True表示有货

def send_telegram_photo(message, has_photo=True):
    """发送截图到Telegram"""
    try:
        if has_photo and os.path.exists(SCREENSHOT_PATH):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            with open(SCREENSHOT_PATH, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': message,
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, files=files, data=data, timeout=10)
        else:
            # 没有截图就发文字
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ 通知已发送")
            return True
        else:
            print(f"❌ 发送失败: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 发送错误: {e}")
        return False

def main():
    print(f"⏰ 检查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 网址: {WEBSITE_URL}")
    
    # 1. 截图
    success, page_text = take_screenshot()
    if not success:
        print("⚠️ 截图失败")
        send_telegram_photo("❌ 网站检查失败，无法截图", has_photo=False)
        return
    
    # 2. 检查库存
    has_stock = check_stock_status(page_text)
    
    # 3. 发送通知
    if has_stock:
        # 🎉 有货了！
        message = f"""🎉 <b>【重要】有货了！！！</b>

🔗 <b>网址：</b> {WEBSITE_URL}

📦 <b>产品：</b> Free Discord Bot Hosting

⏰ <b>检查时间：</b> {time.strftime('%Y-%m-%d %H:%M:%S')}

✅ <b>状态：</b> 可以购买！

立即访问: https://billing.darkless.cloud/products/discord/256mb"""
        print("🎉 发现有货！发送通知...")
    else:
        # 还是缺货
        message = f"""📊 <b>库存检查完成</b>

🔗 <b>网址：</b> {WEBSITE_URL}

📦 <b>产品：</b> Free Discord Bot Hosting

⏰ <b>检查时间：</b> {time.strftime('%Y-%m-%d %H:%M:%S')}

❌ <b>状态：</b> 暂时缺货"""
        print("❌ 仍然缺货")
    
    send_telegram_photo(message)
    
    # 清理
    if os.path.exists(SCREENSHOT_PATH):
        os.remove(SCREENSHOT_PATH)
    
    print("✅ 完成")

if __name__ == "__main__":
    main()
