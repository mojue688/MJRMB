# -*- coding: utf-8 -*-
"""
Watchdog 守护进程 - 持续监控并重启目标程序
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="目标程序完整路径和参数，例如 'C:\\path\\app.exe --persist'")
    parser.add_argument("--interval", type=int, default=2, help="检查间隔秒数")
    args = parser.parse_args()

    target_cmd = args.target
    log(f"启动，监控目标: {target_cmd}")
    env = os.environ.copy()
    env["WATCHDOG_LAUNCHED"] = "1"

    # 首次启动
    proc = subprocess.Popen(target_cmd, shell=True, env=env)

    while True:
        time.sleep(args.interval)
        if proc.poll() is not None:
            log("目标进程已退出，正在重启...")
            proc = subprocess.Popen(target_cmd, shell=True, env=env)
            log("目标进程已重新启动")

if __name__ == "__main__":
    main()