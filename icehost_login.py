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
    print("🔍 启动 CDP 底层注入验证模式...")
    
    # 隐藏 WebDriver 特征
    sb.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    time.sleep(12) 
    
    # 1. 尝试调用 SeleniumBase 内部逻辑
    try:
        print("⚡ 尝试 UC 模式自带验证处理...")
        sb.uc_gui_handle_captcha()
    except:
        pass

    # 2. 如果没跳，执行 CDP 强制物理点击
    print("⏳ 等待并执行强制补点...")
    for i in range(15):
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            print("🎉 验证成功！")
            return True
        
        # 在第 5 步时，发送原始 CDP 鼠标指令
        if i == 5:
            print("🎯 发送 CDP 强制点击指令 (960, 525)")
            try:
                # 这种方式直接操作浏览器内核，不需要 SeleniumBase 的封装函数
                sb.execute_cdp_cmd('Input.dispatchMouseEvent', {
                    'type': 'mousePressed', 'x': 960, 'y': 525, 'button': 'left', 'clickCount': 1
                })
                sb.execute_cdp_cmd('Input.dispatchMouseEvent', {
                    'type': 'mouseReleased', 'x': 960, 'y': 525, 'button': 'left', 'clickCount': 1
                })
            except Exception as e:
                print(f"⚠️ CDP 点击异常: {e}")
            
        if i % 3 == 0:
            sb.save_screenshot(f"cdp_step_{i}.png")
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
