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
    print("🔍 启动修正后的指纹混淆验证模式...")
    
    # 隐藏 WebDriver 特征
    sb.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # 延长初始观察时间
    time.sleep(12) 
    
    # 1. 增加一个“激活页面”的操作：点击页面左上角空白处
    try:
        sb.click_at_raw_coords(10, 10)
        print("🖱️ 已点击空白处激活窗口")
    except:
        pass

    # 2. 调用高级验证码处理器
    try:
        print("⚡ 尝试调用 SeleniumBase 内部逻辑过验证...")
        # 这一步会自动寻找 Turnstile 并模拟物理点击
        sb.uc_gui_handle_captcha()
    except Exception as e:
        print(f"⚠️ 自动处理尝试完毕 (详情: {e})")

    # 3. 循环监测：如果自动处理没过，尝试一次手动坐标点击
    print("⏳ 等待验证响应...")
    for i in range(15):
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print("🎉 验证成功！")
            return True
        
        # 中途补救：尝试点击截图里验证码方框的大致位置
        if i == 5:
            print("🎯 尝试最后一次坐标补点击...")
            # 根据 1920x1080 截图估算的方框位置
            sb.click_at_raw_coords(960, 525) 
            
        if i % 3 == 0:
            sb.save_screenshot(f"final_check_step_{i}.png")
            
        time.sleep(2)
        
    return False

def main():
    # 修正后的参数，删除了不支持的 no_sandbox 等
    options = {
        "uc": True,
        "headless": False, 
        "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    
    if PROXY:
        options["proxy"] = PROXY

    # 启动
    with SB(**options) as sb:
        print("🚀 正在访问 IceHost...")
        try:
            sb.uc_open_with_reconnect(LOGIN_URL, 5)
        except:
            sb.open(LOGIN_URL)

        # 验证码处理
        if not handle_turnstile(sb):
            print("❌ 验证码未能通过，可能是 IP 被识别为数据中心")
            sb.save_screenshot("fail_at_captcha.png")
            return

        # 填写信息
        print("📝 正在填写登录信息...")
        sb.type('input[placeholder="name@skypass.tech"]', EMAIL, timeout=10)
        sb.type('input[type="password"]', PASSWORD, timeout=10)
        sb.click('button[type="submit"]')
        
        # 结果展示
        time.sleep(10)
        sb.save_screenshot("final_result.png")
        print(f"🏁 运行完毕，当前页面: {sb.get_current_url()}")

if __name__ == "__main__":
    main()
