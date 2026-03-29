import os
import time
import random
from seleniumbase import SB

# --- 配置区 ---
LOGIN_URL = "https://dash.icehost.pl/auth/login"
EMAIL = os.environ.get("ICEHOST_EMAIL")
PASSWORD = os.environ.get("ICEHOST_PASSWORD")
PROXY = os.environ.get("PROXY_SOCKS5") 

def handle_turnstile(sb):
    print("🔍 启动指纹混淆与高级验证模式...")
    
    # 隐藏 WebDriver 特征
    sb.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # 给页面足够的“观察”时间，Cloudflare 对立即点击很敏感
    time.sleep(15) 
    
    # 1. 模拟人类鼠标在页面上随意移动
    try:
        print("🖱️ 模拟人类鼠标轨迹...")
        sb.mouse_move(random.randint(100, 500), random.randint(100, 500))
        time.sleep(0.5)
        sb.mouse_move(random.randint(600, 900), random.randint(400, 700))
    except:
        pass

    # 2. 调用高级验证码处理器 (SeleniumBase 核心过人招数)
    try:
        print("⚡ 尝试自动破解验证码方框...")
        sb.uc_gui_handle_captcha()
    except Exception as e:
        print(f"⚠️ 高级处理异常（可能已过或需手动）: {e}")

    # 3. 循环检测跳转结果
    print("⏳ 等待跳转至登录表单...")
    for i in range(15):
        # 检查是否看到了账号输入框
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print("🎉 验证成功通过！")
            return True
        
        # 实时存图，我们可以通过 Artifacts 看到点击后的状态
        if i % 3 == 0:
            sb.save_screenshot(f"verify_step_{i}.png")
            
        time.sleep(2)
        
    return False

def main():
    # 修正后的参数设置
    options = {
        "uc": True,
        "headless": False,  # xvfb 环境下设为 False
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    # 代理设置
    if PROXY:
        options["proxy"] = PROXY

    # 启动浏览器
    # 注意：SeleniumBase 内部会自动处理 --no-sandbox 等参数，无需手动传入
    with SB(**options) as sb:
        print("🚀 正在访问 IceHost 登录页...")
        try:
            sb.uc_open_with_reconnect(LOGIN_URL, 5)
        except:
            sb.open(LOGIN_URL)

        # 执行验证码绕过
        if not handle_turnstile(sb):
            print("❌ 验证码识别超时，可能需要更换更高质量的节点 IP")
            sb.save_screenshot("final_error.png")
            return

        # 填写登录信息
        print("📝 正在填写登录账号...")
        sb.type('input[placeholder="name@skypass.tech"]', EMAIL, timeout=10)
        sb.type('input[type="password"]', PASSWORD, timeout=10)
        sb.save_screenshot("login_filling.png")
        
        # 提交登录
        sb.click('button[type="submit"]')
        
        # 确认结果
        time.sleep(8)
        sb.save_screenshot("login_result.png")
        print(f"🏁 任务结束，最终位置: {sb.get_current_url()}")

if __name__ == "__main__":
    main()
