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
    print("🔍 启动 JavaScript 强行注入验证模式...")
    time.sleep(10) 
    
    # 方案 A: 强制获取 iframe 中心并使用 uc_click (带轨迹模拟)
    try:
        iframe_selector = "iframe[src*='turnstile']"
        if sb.is_element_visible(iframe_selector):
            print("🎯 发现验证码 Iframe，正在模拟真人轨迹点击...")
            # uc_click 比普通 click 更能避开检测
            sb.uc_click(iframe_selector)
            time.sleep(5)
    except Exception as e:
        print(f"⚠️ 轨迹点击失败: {e}")

    # 方案 B: JS 注入——强行改变焦点并回车
    if not sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
        print("⌨️ 尝试 JS 聚焦注入...")
        try:
            # 这段脚本会尝试在所有 iframe 中寻找并点击验证框
            sb.execute_script("""
                var iframes = document.querySelectorAll('iframe');
                for (var i = 0; i < iframes.length; i++) {
                    if (iframes[i].src.indexOf('turnstile') !== -1) {
                        iframes[i].focus();
                        console.log('Focused on Turnstile iframe ' + i);
                    }
                }
            """)
            time.sleep(1)
            sb.press_keys("body", "\n") # 在聚焦状态下按回车
            print("✅ 已执行焦点回车注入")
        except:
            pass

    # 验证跳转
    for i in range(10):
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print("🎉 注入成功，已进入登录页面！")
            return True
        time.sleep(3)
        sb.save_screenshot(f"retry_step_{i}.png")
    
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
