import os
import time
from seleniumbase import SB

# --- 配置区 ---
LOGIN_URL = "https://dash.icehost.pl/auth/login"
RENEW_URL = "https://dash.icehost.pl/clientarea/services" # 续期页面地址
EMAIL = os.environ.get("ICEHOST_EMAIL")
PASSWORD = os.environ.get("ICEHOST_PASSWORD")
PROXY = os.environ.get("PROXY_SOCKS5") 

def handle_turnstile(sb):
    print("🔍 正在尝试破解 Cloudflare 验证码...")
    time.sleep(5) # 等待验证码加载
    
    # 方案 1：尝试 SeleniumBase 自动点击
    try:
        sb.uc_gui_click_captcha()
        print("⚡ 已执行底层 GUI 点击模拟")
    except:
        pass

    # 方案 2：强制穿透 Iframe 点击方框
    if not sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
        try:
            # 找到验证码所在的 Iframe 并跳进去
            sb.switch_to_frame("iframe[title*='verification']")
            print("📥 已进入验证码内部空间")
            
            # 点击那个该死的方框 (#challenge-stage 是 Cloudflare 的标准 ID)
            if sb.is_element_visible('#challenge-stage'):
                sb.click('#challenge-stage')
                print("✅ 已点击验证方框！")
            else:
                # 如果找不到 ID，就点一下页面中心
                sb.click_active_element()
                print("✅ 点击了中心区域")
            
            sb.switch_to_default_content() # 别忘了跳出来
        except Exception as e:
            print(f"ℹ️ Iframe 点击未生效: {e}")
            sb.switch_to_default_content()

    # 等待结果
    print("⏳ 等待跳转至登录表单...")
    for i in range(15):
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print(f"✨ 验证通过！总耗时约 {i*2+5} 秒")
            return True
        time.sleep(2)
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
