import os
import time
from DrissionPage import ChromiumPage, ChromiumOptions

def run_login():
    # 配置浏览器：无头模式并在 Docker/Action 环境中运行的必要参数
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-gpu')
    co.set_argument('--disable-dev-shm-usage')
    co.set_headless(True)  # Actions 必须开启无头模式
    
    # 创建截图目录
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    page = ChromiumPage(co)
    
    try:
        # 第一步：访问页面
        print("Step 1: 正在访问登录页面...")
        page.get('https://dash.icehost.pl/auth/login')
        time.sleep(5) # 等待 Turnstile 加载
        page.get_screenshot(path='screenshots/1_initial_load.png')

        # 第二步：处理 Turnstile
        # DrissionPage 默认会处理大多数隐形验证，如果页面有 iframe，我们尝试点击中心
        print("Step 2: 检测验证码状态...")
        if page.ele('tag:iframe'):
            print("发现 Turnstile 验证框，尝试等待自动通过...")
            # 这里的等待时间建议长一点，Cloudflare 在 Action IP 下验证较慢
            time.sleep(10)
            page.get_screenshot(path='screenshots/2_after_turnstile.png')

        # 第三步：输入登录信息
        print("Step 3: 尝试填写表单...")
        email_input = page.wait.ele_displayed('@placeholder=name@skypass.tech', timeout=20)
        
        if email_input:
            email_input.input(os.environ['ICEHOST_EMAIL'])
            page.ele('@type=password').input(os.environ['ICEHOST_PASSWORD'])
            page.get_screenshot(path='screenshots/3_filled_form.png')
            
            # 点击登录
            page.ele('text=Zaloguj się do panelu').click()
            print("登录按钮已点击。")
            
            # 第四步：确认结果
            time.sleep(8) # 等待跳转
            page.get_screenshot(path='screenshots/4_final_result.png')
            print(f"当前 URL: {page.url}")
            
            if "login" not in page.url:
                print("登录成功！")
            else:
                print("登录失败，可能被 Cloudflare 拦截或账号错误。")
        else:
            print("无法定位登录框，验证码可能未通过。")

    except Exception as e:
        print(f"发生错误: {e}")
        page.get_screenshot(path='screenshots/error.png')
    finally:
        page.quit()

if __name__ == "__main__":
    run_login()
