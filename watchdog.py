# -*- coding: utf-8 -*-

"""
Watchdog 守护进程 - 用于持续监控 Security Demo 主程序
========================================================
功能：
    - 每秒检查主进程是否存活
    - 如果主进程退出，则立即重新启动
    - 自身可通过 Ctrl+C 终止（或手动杀进程）
    - 启动时会设置环境变量 WATCHDOG_LAUNCHED=1，避免主程序再次启动watchdog

用法：
    python watchdog.py --target "python security_demo.py"
    （或者直接监控编译后的 exe）
"""

import sys
import os
import time
import subprocess
import psutil
import argparse
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [WATCHDOG] {msg}")

def find_process_by_cmd(cmd_pattern):
    """通过命令行模式查找进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if cmd_pattern in cmdline:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def main():
    parser = argparse.ArgumentParser(description="Watchdog for Security Demo")
    parser.add_argument("--target", required=True, help="目标程序完整命令行，例如 'python security_demo.py'")
    parser.add_argument("--check-interval", type=int, default=2, help="检查间隔（秒）")
    args = parser.parse_args()

    log(f"Watchdog 启动，监控目标: {args.target}")
    log(f"检查间隔: {args.check_interval} 秒")

    target_cmd = args.target

    # 设置环境变量，通知主程序由 watchdog 启动
    env = os.environ.copy()
    env["WATCHDOG_LAUNCHED"] = "1"

    # 第一次启动
    log("启动目标程序...")
    proc = subprocess.Popen(target_cmd, shell=True, env=env)

    while True:
        time.sleep(args.check_interval)

        # 检查进程是否存活
        if proc.poll() is not None:
            log("目标程序已退出，正在重启...")
            proc = subprocess.Popen(target_cmd, shell=True, env=env)
            log("目标程序已重新启动")

if __name__ == "__main__":
    main()