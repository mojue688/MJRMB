# -*- coding: utf-8 -*-
"""
Watchdog 守护进程 - 用于持续监控 Security Demo 主程序
========================================================
功能：
    - 每秒检查主进程是否存活
    - 如果主进程退出，则立即重新启动
    - 自身可通过 Ctrl+C 终止，退出时连带杀掉被监控主程序
    - 启动时会设置环境变量 WATCHDOG_LAUNCHED=1，避免主程序再次启动watchdog
用法：
    python watchdog.py --target "C:\\xxx\\main.exe"
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

def find_process_by_exe(exe_path: str):
    """根据exe完整路径查找正在运行的目标进程"""
    exe_path = os.path.normcase(os.path.abspath(exe_path))
    for proc in psutil.process_iter(['pid', 'exe']):
        try:
            p_exe = proc.info.get("exe")
            if p_exe and os.path.normcase(p_exe) == exe_path:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def kill_target_proc(proc):
    if proc is None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except psutil.NoSuchProcess:
        pass
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="Watchdog for Security Demo")
    parser.add_argument("--target", required=True, help="目标程序完整exe绝对路径")
    parser.add_argument("--check-interval", type=int, default=2, help="检查间隔（秒）")
    args = parser.parse_args()

    target_exe = os.path.normpath(args.target)
    check_interval = args.check_interval

    log(f"Watchdog 启动，监控目标: {target_exe}")
    log(f"检查间隔: {check_interval} 秒")

    env = os.environ.copy()
    env["WATCHDOG_LAUNCHED"] = "1"

    target_proc = None

    try:
        while True:
            existing = find_process_by_exe(target_exe)
            if existing is not None:
                if target_proc is None or target_proc.pid != existing.pid:
                    log(f"检测到已有正在运行的目标进程 pid={existing.pid}，复用")
                    target_proc = existing
            else:
                if target_proc is None or target_proc.poll() is not None:
                    log("目标进程不存在/已退出，启动主程序...")
                    target_proc = subprocess.Popen(
                        [target_exe],
                        env=env,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        close_fds=True
                    )
                    log(f"目标程序已启动 pid={target_proc.pid}")
            time.sleep(check_interval)

    except KeyboardInterrupt:
        log("收到 Ctrl+C，watchdog准备退出，清理目标进程")
        kill_target_proc(target_proc)
    except Exception as e:
        log(f"Watchdog发生异常: {str(e)}")
        kill_target_proc(target_proc)
        sys.exit(1)

if __name__ == "__main__":
    main()
