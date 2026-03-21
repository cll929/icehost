#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import subprocess
from seleniumbase import SB

# 配置与 JS 注入 (基于你的物理点击模板)
_COORDS_JS = """(function(){var iframes=document.querySelectorAll('iframe');for(var i=0;i<iframes.length;i++){var src=iframes[i].src||'';if(src.includes('cloudflare')||src.includes('turnstile')){var r=iframes[i].getBoundingClientRect();if(r.width>0&&r.height>0)return {cx:Math.round(r.x+30),cy:Math.round(r.y+r.height/2)};}}return null;})()"""
_WININFO_JS = """(function(){return {sx:window.screenX||0,sy:window.screenY||0,oh:window.outerHeight,ih:window.innerHeight};})()"""

def physical_click(x, y):
    subprocess.run(["xdotool", "mousemove", "--sync", str(x), str(y)], check=True)
    time.sleep(0.2)
    subprocess.run(["xdotool", "click", "1"], check=True)

def run_task():
    # uc=True 必须开启以规避检测
    with SB(uc=True, test=True, headless=False) as sb:
        url = "https://dash.icehost.pl"
        
        # 步骤 1: 访问首页
        print(f"🚀 正在访问: {url}")
        sb.uc_open_with_reconnect(url, reconnect_time=5)
        time.sleep(5)
        sb.save_screenshot("step1_initial_load.png")

        # 步骤 2: 判断并处理 Cloudflare
        current_url = sb.get_current_url()
        if "login" not in current_url:
            print("🛡️ 检测到人机验证页，尝试破解...")
            
            for attempt in range(5):
                coords = sb.execute_script(_COORDS_JS)
                if coords:
                    wi = sb.execute_script(_WININFO_JS)
                    # GitHub Actions 的虚拟窗口通常没有复杂的边框，但计算逻辑保留以防万一
                    bar = wi["oh"] - wi["ih"]
                    ax, ay = coords["cx"] + wi["sx"], coords["cy"] + wi["sy"] + bar
                    
                    print(f"🖱️ 第 {attempt+1} 次尝试物理点击: ({ax}, {ay})")
                    physical_click(ax, ay)
                    
                    # 点击后等待 5 秒观察是否跳转
                    time.sleep(5)
                    sb.save_screenshot(f"step2_after_click_attempt_{attempt+1}.png")
                    
                    if "login" in sb.get_current_url():
                        print("✅ 验证成功，已进入登录页面！")
                        break
                else:
                    print("⏳ 未找到验证框，重试中...")
                    time.sleep(3)
        
        # 步骤 3: 确认最终状态
        final_url = sb.get_current_url()
        sb.save_screenshot("step3_final_state.png")
        
        if "login" in final_url:
            print(f"🎉 任务第一阶段成功：当前 URL 为 {final_url}")
            # 这里可以继续编写 email 和 password 的填写逻辑
        else:
            print("❌ 任务失败：未能跳转到登录页")
            exit(1)

if __name__ == "__main__":
    run_task()
