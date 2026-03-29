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
    print("🔍 进入高级扫描探测模式...")
    time.sleep(10) # 确保 iframe 彻底加载完毕
    
    # 扫描点阵：针对 1920x1080 分辨率下的验证码框位置
    # 验证码方框通常位于页面正中心区域
    click_points = [
        (960, 520), (940, 520), (980, 520), # 横向扫描
        (960, 500), (960, 540)              # 纵向扫描
    ]

    for idx, (x, y) in enumerate(click_points):
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            return True
            
        print(f"🎯 尝试探测点击点 {idx+1}: ({x}, {y})")
        try:
            # 使用 SeleniumBase 的物理模拟点击
            sb.click_at_raw_coords(x, y)
            time.sleep(3) # 每次点击后多等一会儿看反应
        except:
            continue
            
        # 实时保存截图，观察点击后复选框是否有“打钩”迹象
        sb.save_screenshot(f"scan_attempt_{idx}.png")
        
        if "auth/login" in sb.get_current_url():
            print("✨ 检测到 URL 跳转，验证可能已通过！")
            return True

    # 兜底方案：尝试通过键盘 Tab 键循环聚焦
    print("⌨️ 坐标点击无果，尝试 Tab 键循环盲点...")
    for _ in range(5):
        sb.press_keys("body", "\t")
        time.sleep(0.5)
        sb.press_keys("body", " ")
        time.sleep(2)
        if sb.is_element_visible('input[placeholder="name@skypass.tech"]'):
            return True

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
