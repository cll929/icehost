import os
import time
from seleniumbase import SB

# --- 配置区 ---
LOGIN_URL = "https://dash.icehost.pl/auth/login"
RENEW_URL = "https://dash.icehost.pl/clientarea/services" # 续期页面地址
EMAIL = os.environ.get("ICEHOST_EMAIL")
PASSWORD = os.environ.get("ICEHOST_PASSWORD")
PROXY = os.environ.get("PROXY_SOCKS5") 

import random

def handle_turnstile(sb):
    print("🔍 启动物理坐标 + Iframe 深度探测模式...")
    time.sleep(12) # 给 Turnstile 充足的时间生成 token

    # 1. 尝试定位 iframe 的实际屏幕位置
    try:
        # 获取 iframe 的位置信息
        iframe_selector = "iframe[src*='turnstile']"
        if sb.is_element_present(iframe_selector):
            # 获取元素中心点
            location = sb.get_element(iframe_selector).location
            size = sb.get_element(iframe_selector).size
            
            # 计算点击中心 (通常复选框在左侧)
            center_x = location['x'] + 30  # 稍微偏左，通常是方框位置
            center_y = location['y'] + (size['height'] / 2)
            
            print(f"📍 检测到验证码 Iframe 位置: {location}, 尝试点击: ({center_x}, {center_y})")
            
            # 在中心点附近进行 3 次带随机偏移的点击
            for i in range(3):
                offset_x = center_x + random.randint(-5, 5)
                offset_y = center_y + random.randint(-5, 5)
                sb.click_at_raw_coords(offset_x, offset_y)
                print(f"   👉 尝试偏移点击 {i+1}: ({offset_x}, {offset_y})")
                time.sleep(3)
                if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
                    return True
    except Exception as e:
        print(f"⚠️ 定位 Iframe 失败: {e}")

    # 2. 如果坐标点击失效，尝试最原始的“盲人摸象”：Tab 键配合 Enter
    print("⌨️ 坐标点击失效，尝试键盘序列注入...")
    try:
        # 点击页面空白处激活窗口
        sb.click_at_raw_coords(10, 10)
        time.sleep(1)
        # 不同的网站 Tab 次数不同，我们多试几次
        for t in range(5, 9): 
            sb.press_keys("body", "\t" * t)
            time.sleep(0.5)
            sb.press_keys("body", "\n") # 回车键
            print(f"   🎹 尝试第 {t} 次 Tab 序列...")
            time.sleep(4)
            if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
                return True
    except:
        pass

    return False

def main():
    # 启动设置
    options = {
        "uc": True,
        "headless": True,
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    if PROXY:
        options["proxy"] = PROXY

    with SB(**options) as sb:
        print("🚀 正在通过代理访问 IceHost...")
        sb.uc_open_with_reconnect(LOGIN_URL, 5)
        sb.save_screenshot("1_open_page.png")

        # 1. 过验证码
        if not handle_turnstile(sb):
            print("❌ 验证码识别超时，请检查节点质量")
            sb.save_screenshot("error_turnstile.png")
            return

        # 2. 登录
        print("📝 正在输入账号密码...")
        sb.type('input[placeholder="name@skypass.tech"]', EMAIL)
        sb.type('input[type="password"]', PASSWORD)
        sb.click('button:contains("Zaloguj się do panelu")')
        
        # 3. 检查登录结果并寻找续期按钮
        time.sleep(5)
        sb.save_screenshot("2_after_login.png")
        
        if "auth/login" not in sb.get_current_url():
            print("🎉 登录成功！正在寻找续期按钮...")
            # 这里是自动续期的逻辑代码（根据 IceHost 页面结构）
            # sb.open(RENEW_URL) 
            # ... 继续添加点击续期的代码 ...
        else:
            print("❌ 登录失败，请检查账号密码")

if __name__ == "__main__":
    main()
