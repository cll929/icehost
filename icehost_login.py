import os
import time
from seleniumbase import SB

# 配置
LOGIN_URL = "https://dash.icehost.pl/auth/login"
EMAIL = os.environ.get("ICEHOST_EMAIL")
PASSWORD = os.environ.get("ICEHOST_PASSWORD")
PROXY = os.environ.get("PROXY_SOCKS5") # 从 Actions 环境变量获取

def handle_turnstile(sb):
    print("🔍 正在检测 Cloudflare Turnstile...")
    time.sleep(3)
    # 使用 seleniumbase 内置的 uc_gui_click_captcha 尝试自动处理
    try:
        sb.uc_gui_click_captcha()
        print("✅ 尝试完成物理点击验证")
    except:
        print("ℹ️ 未触发自动点击，尝试静默等待...")
    
    # 等待验证成功（登录框出现）
    for i in range(10):
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print(f"✅ 验证通过 (尝试第 {i+1} 次)")
            return True
        time.sleep(2)
    return False

def main():
    if not EMAIL or not PASSWORD:
        print("❌ 错误：未配置账户环境变量")
        return

    # 启动配置
    sb_args = {
        "uc": True,
        "test": True,
        "headless": True, # Actions 必须开启
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    if PROXY:
        sb_args["proxy"] = PROXY
        print(f"🌐 使用代理: {PROXY}")

    with SB(**sb_args) as sb:
        print("🚀 正在打开 IceHost...")
        sb.uc_open_with_reconnect(LOGIN_URL, 5)
        sb.save_screenshot("1_load_page.png")

        # 检查是否依然被 WAF 拦截
        if "Connection Blocked" in sb.get_page_source():
            print("❌ 拦截失败：当前代理 IP 依然被 IceHost 封锁！")
            return

        # 处理验证码
        if not handle_turnstile(sb):
            print("❌ 验证码识别超时")
            sb.save_screenshot("error_turnstile.png")
            return

        # 填写表单
        print("📝 正在填写登录信息...")
        sb.type('input[placeholder="name@skypass.tech"]', EMAIL)
        sb.type('input[type="password"]', PASSWORD)
        sb.save_screenshot("2_before_login.png")
        
        # 提交
        sb.click('button:contains("Zaloguj się do panelu")')
        
        # 验证跳转
        time.sleep(5)
        sb.save_screenshot("3_after_login.png")
        
        if "auth/login" not in sb.get_current_url():
            print("🎉 登录成功！")
            # 这里可以继续添加跳转到续期页面的逻辑
        else:
            print("❌ 登录失败，请检查账号密码或截图")

if __name__ == "__main__":
    main()
