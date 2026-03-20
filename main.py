#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, time, random, requests
from seleniumbase import SB

ACCOUNTS = os.environ.get("ACCOUNTS")  # 格式: 邮箱:密码;邮箱:密码
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_CHAT_ID   = os.environ.get("TG_CHAT_ID")

def mask_email(email: str) -> str:
    try:
        name, domain = email.split("@", 1)
        if len(name) <= 3:
            masked = name[0] + "***"
        else:
            masked = name[:3] + "***"
        return f"{masked}@{domain}"
    except:
        return "未知账号"
# =========================
# Telegram
# =========================
def send(msg):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        print(msg)
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass

# =========================
# Turnstile 检测
# =========================
def has_cf(sb):
    try:
        return sb.execute_script(
            'return document.querySelector("input[name=cf-turnstile-response]")!=null'
        )
    except:
        return False

def solve_cf(sb):
    print("🛡️ 尝试通过 CF...")
    for i in range(6):
        time.sleep(2)
        if not has_cf(sb):
            return True
        try:
            sb.click("iframe")
        except:
            pass
    return not has_cf(sb)

# =========================
# 登录
# =========================
def login(sb, email, pwd):
    sb.open("https://dash.icehost.pl")
    time.sleep(5)

    if has_cf(sb):
        if not solve_cf(sb):
            return False

    for _ in range(15):
        time.sleep(1)
        if "/auth/login" in sb.get_current_url():
            break

    sb.type('input[type="email"]', email)
    sb.type('input[type="password"]', pwd)

    if has_cf(sb):
        if not solve_cf(sb):
            return False

    sb.click('button:contains("Zaloguj")')

    for _ in range(15):
        time.sleep(1)
        if "/server/" in sb.get_current_url():
            return True

    return False

# =========================
# 续期逻辑
# =========================
def renew(sb, email):
    time.sleep(3)

    # ❗ 冷却检测
    try:
        err = sb.get_text('div:contains("Nie możesz przedłużyć")')
        if err:
            send(f"⏸️ {mask_email(email)}\n冷却中，跳过续期")
            return True
    except:
        pass

    # ❗ 找按钮
    try:
        sb.wait_for_element('button:contains("DODAJ 6 GODZIN")', timeout=10)
    except:
        send(f"❌ {email}\n未找到续期按钮")
        sb.save_screenshot(f"{email}_no_btn.png")
        return False

    # ❗ 点击
    sb.click('button:contains("DODAJ 6 GODZIN")')
    time.sleep(4)

    # ❗ 再检测冷却
    try:
        err = sb.get_text('div:contains("Nie możesz przedłużyć")')
        if err:
            send(f"⏸️ {email}\n冷却中（点击后检测）")
            return True
    except:
        pass

    # ✅ 成功
    sb.save_screenshot(f"{email}_success.png")
    send(f"✅ {mask_email(email)}\n续期成功 +6小时")
    return True

# =========================
# 主流程（多账号）
# =========================
def main():
    if not ACCOUNTS:
        print("❌ 未设置 ACCOUNTS")
        return

    accounts = [a.strip() for a in ACCOUNTS.split(";") if a.strip()]

    for acc in accounts:
        email, pwd = acc.split(":", 1)

        print(f"\n👤 开始处理: {email}")

        delay = random.randint(60, 300)
        print(f"⏳ 延迟 {delay}s")
        time.sleep(delay)

        with SB(uc=True, headless=True) as sb:
            try:
                if login(sb, email, pwd):
                    renew(sb, email)
                else:
                    send(f"❌ {mask_email(email)}\n登录失败")
            except Exception as e:
                send(f"❌ {mask_email(email)}\n异常: {e}")

if __name__ == "__main__":
    main()
