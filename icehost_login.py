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
    print("🔍 启动暴力破解 Cloudflare 流程...")
    time.sleep(8) # 延长初始等待，确保网页加载全
    
    # 尝试 1：使用 SeleniumBase 专门对抗 CF 的高级点击
    try:
        sb.uc_gui_click_captcha()
        print("⚡ 已尝试底层智能点击")
    except:
        pass

    # 尝试 2：全页面寻找 iframe 并盲点中心
    if not sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
        try:
            print("🧪 正在尝试通过坐标盲点...")
            # 获取页面中心坐标 (基于 1920x1080)
            # Cloudflare 验证码通常出现在屏幕中间靠下一点的位置
            sb.click_active_element() # 点击当前焦点
            sb.mouse_click(960, 500)  # 尝试点击屏幕中心位置
            print("✅ 已执行坐标盲点 (960, 500)")
        except Exception as e:
            print(f"ℹ️ 坐标点击异常: {e}")

    # 尝试 3：强制刷新验证 (针对卡死状态)
    if not sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
        print("🔄 尝试模拟按下 TAB 和 SPACE (常用绕过手段)")
        try:
            sb.press_keys("body", "\t") # 按下 Tab 键切换焦点
            time.sleep(1)
            sb.press_keys("body", " ")  # 按下空格键尝试激活方框
        except:
            pass

    # 等待结果
    print("⏳ 等待跳转结果...")
    for i in range(20): # 增加到 40 秒等待
        curr_url = sb.get_current_url()
        if "auth/login" in curr_url and sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print(f"✨ 终于进来了！(耗时 {i*2+8}s)")
            return True
        if i % 5 == 0:
            sb.save_screenshot(f"debug_step_{i}.png") # 每 10 秒存一张图看看进度
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
