# -*- coding: utf-8 -*-

"""
网络安全演练 UI
========================================================
安全演示版本

功能：
    - 全屏显示
    - 大尺寸中央面板
    - 红色边框
    - 演练徽章
    - 右上角实时本机信息
    - 自动获取本机 IPv4
    - 自动获取电脑名称
    - 自动获取当前时区
    - 自动获取当前系统时间
    - 72 小时演练倒计时
    - ESC 安全退出
    - Ctrl + Shift + Q 连续 3 次退出

注意：
    本程序不上传网络信息。
    不获取 GPS。
    不获取精确家庭/街道位置。
    不包含真实付款、文件删除、文件加密等功能。
"""

import tkinter as tk
from tkinter import messagebox

import socket
import time
import random
import string
import math
import platform

from datetime import datetime, timedelta


# ============================================================
# 页面配置
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
# 工具
# ============================================================

def generate_demo_id():
    """
    生成演练编号
    """

    chars = (
        string.ascii_uppercase
        + string.digits
    )

    return "".join(
        random.choice(chars)
        for _ in range(10)
    )


def get_local_ip():
    """
    获取当前电脑局域网 IPv4

    不向外部服务器发送数据。
    """

    ip = "127.0.0.1"

    sock = None

    try:

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        # UDP connect 不会真的发送数据。
        # 用于让系统选择当前默认网卡。
        sock.connect(
            ("8.8.8.8", 80)
        )

        ip = sock.getsockname()[0]

    except Exception:

        try:

            hostname = socket.gethostname()

            ip = socket.gethostbyname(
                hostname
            )

        except Exception:

            ip = "127.0.0.1"

    finally:

        if sock:

            sock.close()

    return ip


def get_hostname():
    """
    获取电脑名称
    """

    try:

        return socket.gethostname()

    except Exception:

        return "UNKNOWN-PC"


def get_timezone():
    """
    获取当前系统时区。

    Python 3.9+ 通常可以通过：
        datetime.now().astimezone().tzinfo

    获取本机时区信息。
    """

    try:

        current = (
            datetime
            .now()
            .astimezone()
        )

        tz = current.tzinfo

        if tz:

            tz_name = str(tz)

            if tz_name:

                return tz_name

    except Exception:

        pass

    return "Local Time"


def get_current_time():
    """
    返回当前时间字符串
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def log(message):
    """
    控制台日志
    """

    print(
        "[{}] {}".format(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            message
        )
    )


# ============================================================
# 主 UI
# ============================================================

class SecurityDemoUI:

    def __init__(self):

        # ----------------------------------------------------
        # 创建窗口
        # ----------------------------------------------------

        self.root = tk.Tk()

        self.root.title(
            "网络安全演练"
        )

        self.root.configure(
            bg=WINDOW_BG
        )

        # ----------------------------------------------------
        # 无标题栏
        # ----------------------------------------------------

        self.root.overrideredirect(
            True
        )

        # ----------------------------------------------------
        # 置顶
        # ----------------------------------------------------

        self.root.attributes(
            "-topmost",
            True
        )

        # ----------------------------------------------------
        # 全屏
        # ----------------------------------------------------

        try:

            self.root.attributes(
                "-fullscreen",
                True
            )

        except Exception:

            width = (
                self.root.winfo_screenwidth()
            )

            height = (
                self.root.winfo_screenheight()
            )

            self.root.geometry(
                f"{width}x{height}+0+0"
            )

        # ----------------------------------------------------
        # 屏幕尺寸
        # ----------------------------------------------------

        self.screen_width = (
            self.root.winfo_screenwidth()
        )

        self.screen_height = (
            self.root.winfo_screenheight()
        )

        # ----------------------------------------------------
        # 演练编号
        # ----------------------------------------------------

        self.demo_id = (
            generate_demo_id()
        )

        # ----------------------------------------------------
        # 实时本机信息
        # ----------------------------------------------------

        self.local_ip = (
            get_local_ip()
        )

        self.hostname = (
            get_hostname()
        )

        self.timezone = (
            get_timezone()
        )

        # ----------------------------------------------------
        # 倒计时
        # ----------------------------------------------------

        self.countdown_end = (
            datetime.now()
            + timedelta(hours=72)
        )

        # ----------------------------------------------------
        # 快捷键退出计数
        # ----------------------------------------------------

        self.exit_count = 0

        self.last_exit_press = 0

        log(
            "======================================"
        )

        log(
            "Security Demo UI 启动"
        )

        log(
            f"本机 IP：{self.local_ip}"
        )

        log(
            f"电脑名称：{self.hostname}"
        )

        log(
            f"系统时区：{self.timezone}"
        )

        # ----------------------------------------------------
        # 创建界面
        # ----------------------------------------------------

        self.build_gui()

        # ----------------------------------------------------
        # 更新数据
        # ----------------------------------------------------

        self.update_live_info()

        self.update_countdown()

        # ----------------------------------------------------
        # ESC
        # ----------------------------------------------------

        self.root.bind(
            "<Escape>",
            self.safe_exit
        )

        # ----------------------------------------------------
        # Ctrl + Shift + Q
        # ----------------------------------------------------

        self.root.bind(
            "<Control-Shift-Q>",
            self.exit_shortcut
        )

        self.root.bind(
            "<Control-Shift-q>",
            self.exit_shortcut
        )


    # ========================================================
    # 创建 GUI
    # ========================================================

    def build_gui(self):

        # ----------------------------------------------------
        # 黑色背景
        # ----------------------------------------------------

        background = tk.Frame(
            self.root,
            bg=WINDOW_BG
        )

        background.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # 中央面板位置
        # ----------------------------------------------------

        panel_x = (
            self.screen_width
            - PANEL_WIDTH
        ) // 2

        panel_y = (
            self.screen_height
            - PANEL_HEIGHT
        ) // 2

        # ----------------------------------------------------
        # 白色主体
        # ----------------------------------------------------

        self.panel = tk.Frame(
            self.root,
            bg=WHITE,
            highlightbackground=RED,
            highlightcolor=RED,
            highlightthickness=5
        )

        self.panel.place(
            x=panel_x,
            y=panel_y,
            width=PANEL_WIDTH,
            height=PANEL_HEIGHT
        )

        # ----------------------------------------------------
        # 顶部
        # ----------------------------------------------------

        self.create_top()

        # ----------------------------------------------------
        # 主体
        # ----------------------------------------------------

        self.create_body()

        # ----------------------------------------------------
        # 左下角
        # ----------------------------------------------------

        tk.Label(
            self.root,
            text=(
                "SECURITY TRAINING DEMO    "
                f"ID: {self.demo_id}"
            ),
            font=(
                "Consolas",
                8
            ),
            fg="#777777",
            bg=WINDOW_BG
        ).place(
            x=12,
            y=self.screen_height - 25
        )


    # ========================================================
    # 顶部区域
    # ========================================================

    def create_top(self):

        top = tk.Frame(
            self.panel,
            bg=WHITE
        )

        top.place(
            x=18,
            y=18,
            width=PANEL_WIDTH - 36,
            height=180
        )

        # ----------------------------------------------------
        # 左侧徽章
        # ----------------------------------------------------

        self.create_badge(
            top
        )

        # ----------------------------------------------------
        # 右侧状态
        # ----------------------------------------------------

        self.create_status_box(
            top
        )


    # ========================================================
    # 演练徽章
    # ========================================================

    def create_badge(self, parent):

        canvas = tk.Canvas(
            parent,
            width=165,
            height=165,
            bg=WHITE,
            highlightthickness=0
        )

        canvas.place(
            x=5,
            y=2
        )

        # 外圈
        canvas.create_oval(
            5,
            5,
            160,
            160,
            fill="#E3E3E3",
            outline="#B0B0B0",
            width=2
        )

        # 金色
        canvas.create_oval(
            15,
            15,
            150,
            150,
            fill="#E6C900",
            outline="#9B8700",
            width=2
        )

        # 红色
        canvas.create_oval(
            27,
            27,
            138,
            138,
            fill="#D51920",
            outline="#A30000",
            width=2
        )

        # 大星星
        self.draw_star(
            canvas,
            82,
            57,
            25,
            "#FFD900"
        )

        # 小星星
        stars = [
            (51, 77, 9),
            (114, 77, 9),
            (59, 104, 8),
            (106, 104, 8),
        ]

        for x, y, r in stars:

            self.draw_star(
                canvas,
                x,
                y,
                r,
                "#FFD900"
            )

        # 文字
        canvas.create_text(
            82,
            124,
            text="安全演练",
            font=(
                "Microsoft YaHei",
                14,
                "bold"
            ),
            fill="#FFD900"
        )


    # ========================================================
    # 五角星
    # ========================================================

    def draw_star(
        self,
        canvas,
        cx,
        cy,
        radius,
        color
    ):

        points = []

        for i in range(10):

            angle = (
                math.pi / 2
                + i * math.pi / 5
            )

            if i % 2 == 0:

                r = radius

            else:

                r = radius * 0.42

            x = (
                cx
                + r * math.cos(angle)
            )

            y = (
                cy
                - r * math.sin(angle)
            )

            points.extend(
                [x, y]
            )

        canvas.create_polygon(
            points,
            fill=color,
            outline=color
        )


    # ========================================================
    # 右上状态框
    # ========================================================

    def create_status_box(self, parent):

        self.status_box = tk.Frame(
            parent,
            bg=GRAY,
            relief="solid",
            bd=1
        )

        self.status_box.place(
            x=745,
            y=8,
            width=340,
            height=158
        )

        # ----------------------------------------------------
        # 第一行
        # ----------------------------------------------------

        self.create_status_row(
            0,
            "演练状态：",
            "进行中",
            GREEN
        )

        # ----------------------------------------------------
        # IP
        # ----------------------------------------------------

        self.ip_value = (
            self.create_status_row(
                1,
                "本机 IP：",
                self.local_ip,
                GREEN
            )
        )

        # ----------------------------------------------------
        # 电脑名称
        # ----------------------------------------------------

        self.hostname_value = (
            self.create_status_row(
                2,
                "设备名称：",
                self.hostname,
                BLACK
            )
        )

        # ----------------------------------------------------
        # 时区
        # ----------------------------------------------------

        self.timezone_value = (
            self.create_status_row(
                3,
                "当前时区：",
                self.timezone,
                BLACK
            )
        )

        # ----------------------------------------------------
        # 当前时间
        # ----------------------------------------------------

        self.time_value = (
            self.create_status_row(
                4,
                "当前时间：",
                get_current_time(),
                DARK_RED
            )
        )


    # ========================================================
    # 状态行
    # ========================================================

    def create_status_row(
        self,
        index,
        label,
        value,
        color
    ):

        y = (
            10
            + index * 28
        )

        # 左侧
        tk.Label(
            self.status_box,
            text=label,
            font=(
                "Microsoft YaHei",
                12
            ),
            bg=GRAY,
            fg="#111111",
            anchor="w"
        ).place(
            x=10,
            y=y,
            width=105
        )

        # 右侧
        value_label = tk.Label(
            self.status_box,
            text=value,
            font=(
                "Microsoft YaHei",
                12,
                "bold"
            ),
            bg=GRAY,
            fg=color,
            anchor="w"
        )

        value_label.place(
            x=118,
            y=y,
            width=210
        )

        return value_label


    # ========================================================
    # 主体
    # ========================================================

    def create_body(self):

        body = tk.Frame(
            self.panel,
            bg=WHITE
        )

        body.place(
            x=20,
            y=200,
            width=PANEL_WIDTH - 40,
            height=500
        )

        # ----------------------------------------------------
        # 警告条
        # ----------------------------------------------------

        self.create_warning_banner(
            body
        )

        # ----------------------------------------------------
        # 标题
        # ----------------------------------------------------

        self.create_title(
            body
        )

        # ----------------------------------------------------
        # 正文
        # ----------------------------------------------------

        self.create_description(
            body
        )

        # ----------------------------------------------------
        # 按钮
        # ----------------------------------------------------

        self.create_button(
            body
        )

        # ----------------------------------------------------
        # 底部
        # ----------------------------------------------------

        self.create_notice(
            body
        )


    # ========================================================
    # 警告区域
    # ========================================================

    def create_warning_banner(self, parent):

        # 阴影
        tk.Frame(
            parent,
            bg="#BBBBEE"
        ).place(
            x=15,
            y=15,
            width=420,
            height=110
        )

        canvas = tk.Canvas(
            parent,
            width=420,
            height=110,
            bg=WHITE,
            highlightthickness=0
        )

        canvas.place(
            x=5,
            y=5
        )

        # 外边框
        for i in range(6, 1, -1):

            canvas.create_rectangle(
                i,
                i,
                420 - i,
                110 - i,
                outline="#7777FF",
                width=1
            )

        # 红色部分
        canvas.create_rectangle(
            5,
            5,
            210,
            105,
            fill="#D5003D",
            outline=""
        )

        # 蓝色部分
        canvas.create_rectangle(
            210,
            5,
            415,
            105,
            fill=BLUE,
            outline=""
        )

        # 中间文字
        canvas.create_text(
            210,
            55,
            text="你的电脑已被锁定！",
            font=(
                "Microsoft YaHei",
                26,
                "bold"
            ),
            fill=WHITE
        )


    # ========================================================
    # 标题
    # ========================================================

    def create_title(self, parent):

        tk.Label(
            parent,
            text=(
                "演练编号："
                f"{self.demo_id}"
            ),
            font=(
                "Microsoft YaHei",
                25,
                "bold"
            ),
            bg=WHITE,
            fg="#006000",
            anchor="w"
        ).place(
            x=465,
            y=12
        )

        tk.Label(
            parent,
            text="模拟事件",
            font=(
                "Microsoft YaHei",
                33,
                "bold"
            ),
            bg=WHITE,
            fg=BLACK,
            anchor="w"
        ).place(
            x=465,
            y=62
        )

        tk.Label(
            parent,
            text="800元",
            font=(
                "Microsoft YaHei",
                30,
                "bold"
            ),
            bg=WHITE,
            fg=DARK_RED,
            anchor="w"
        ).place(
            x=710,
            y=61
        )


    # ========================================================
    # 正文
    # ========================================================

    def create_description(self, parent):

        text = (
            "本页面为网络安全课堂演练界面，用于模拟终端遭遇恶意锁定后的视觉效果。\n"
            "\n"
            "页面中的编号、金额、设备状态及倒计时均为虚构数据。\n"
            "\n"
            "右上角的本机 IP、设备名称、时区以及时间来自当前电脑本地环境。\n"
            "这些数据仅用于演示，不会发送到远程服务器。\n"
            "\n"
            "演练目的：帮助学习者识别仿冒执法机构、虚假处罚以及勒索类社会工程学攻击。"
        )

        tk.Label(
            parent,
            text=text,
            font=(
                "Microsoft YaHei",
                15
            ),
            bg=WHITE,
            fg="#111111",
            justify="left",
            anchor="nw",
            wraplength=1030
        ).place(
            x=12,
            y=140,
            width=1030,
            height=170
        )


    # ========================================================
    # 按钮
    # ========================================================

    def create_button(self, parent):

        # 阴影
        tk.Frame(
            parent,
            bg="#D0D0D0"
        ).place(
            x=444,
            y=320,
            width=245,
            height=66
        )

        # 按钮
        button = tk.Button(
            parent,
            text="查看演练说明",
            font=(
                "Microsoft YaHei",
                16,
                "bold"
            ),
            fg=WHITE,
            bg="#9D0000",
            activeforeground=WHITE,
            activebackground="#CC0000",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.show_demo_info
        )

        button.place(
            x=438,
            y=314,
            width=245,
            height=66
        )


    # ========================================================
    # 底部提示
    # ========================================================

    def create_notice(self, parent):

        # 标题
        tk.Label(
            parent,
            text="重要提示！",
            font=(
                "Microsoft YaHei",
                18,
                "bold"
            ),
            bg=WHITE,
            fg=DARK_RED
        ).place(
            x=0,
            y=405,
            width=1060,
            height=32
        )

        # 正文
        notice = (
            "这是网络安全培训模拟页面，不是真实公安机关通知，也不涉及任何真实罚款。\n"
            "页面不会删除文件，不会上传个人信息，也不会进行任何真实支付操作。\n"
            "此界面仅用于帮助学习者识别仿冒执法机构、虚假处罚以及勒索类页面。"
        )

        tk.Label(
            parent,
            text=notice,
            font=(
                "Microsoft YaHei",
                13
            ),
            bg=WHITE,
            fg=DARK_RED,
            justify="center",
            anchor="center",
            wraplength=1030
        ).place(
            x=20,
            y=440,
            width=1020,
            height=80
        )

        # 演练计时
        tk.Label(
            parent,
            text="演练计时：",
            font=(
                "Microsoft YaHei",
                13,
                "bold"
            ),
            bg=WHITE,
            fg=BLACK
        ).place(
            x=440,
            y=505
        )

        self.countdown_label = tk.Label(
            parent,
            text="72:00:00",
            font=(
                "Consolas",
                18,
                "bold"
            ),
            bg=WHITE,
            fg=DARK_RED
        )

        self.countdown_label.place(
            x=545,
            y=503
        )

        # 退出提示
        tk.Label(
            parent,
            text=(
                "ESC 安全退出    |    "
                "Ctrl + Shift + Q 连续 3 次退出"
            ),
            font=(
                "Microsoft YaHei",
                9
            ),
            bg=WHITE,
            fg="#777777"
        ).place(
            x=0,
            y=540,
            width=1060
        )


    # ========================================================
    # 实时更新右上角信息
    # ========================================================

    def update_live_info(self):

        try:

            # ------------------------------------------------
            # IP
            # ------------------------------------------------

            new_ip = get_local_ip()

            if new_ip != self.local_ip:

                self.local_ip = new_ip

                self.ip_value.config(
                    text=new_ip
                )

            # ------------------------------------------------
            # 主机名
            # ------------------------------------------------

            self.hostname_value.config(
                text=get_hostname()
            )

            # ------------------------------------------------
            # 时区
            # ------------------------------------------------

            self.timezone_value.config(
                text=get_timezone()
            )

            # ------------------------------------------------
            # 当前时间
            # ------------------------------------------------

            self.time_value.config(
                text=get_current_time()
            )

        except Exception as error:

            log(
                f"实时信息更新失败：{error}"
            )

        # 每 2 秒刷新一次
        self.root.after(
            2000,
            self.update_live_info
        )


    # ========================================================
    # 倒计时
    # ========================================================

    def update_countdown(self):

        remaining = (
            self.countdown_end
            - datetime.now()
        )

        seconds = int(
            remaining.total_seconds()
        )

        if seconds <= 0:

            self.countdown_label.config(
                text="00:00:00"
            )

            return

        hours, remainder = divmod(
            seconds,
            3600
        )

        minutes, seconds = divmod(
            remainder,
            60
        )

        self.countdown_label.config(
            text=(
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )
        )

        self.root.after(
            1000,
            self.update_countdown
        )


    # ========================================================
    # 演练说明
    # ========================================================

    def show_demo_info(self):

        messagebox.showinfo(
            "网络安全演练",
            (
                "本页面仅用于网络安全教学演示。\n\n"
                f"演练编号：{self.demo_id}\n\n"
                f"本机 IP：{self.local_ip}\n\n"
                f"设备名称：{self.hostname}\n\n"
                f"时区：{self.timezone}\n\n"
                "以上信息来自本机环境。\n"
                "不会上传到远程服务器。\n"
                "不会进行真实支付。"
            ),
            parent=self.root
        )


    # ========================================================
    # ESC 退出
    # ========================================================

    def safe_exit(self, event=None):

        log(
            "ESC 安全退出"
        )

        self.root.destroy()


    # ========================================================
    # Ctrl + Shift + Q
    # ========================================================

    def exit_shortcut(self, event=None):

        now = time.time()

        # 超过两秒重新计算
        if (
            now
            - self.last_exit_press
            > 2
        ):

            self.exit_count = 0

        self.last_exit_press = now

        self.exit_count += 1

        log(
            "退出快捷键："
            f"{self.exit_count}/3"
        )

        if self.exit_count >= 3:

            log(
                "安全退出"
            )

            self.root.destroy()


    # ========================================================
    # 运行
    # ========================================================

    def run(self):

        self.root.mainloop()


# ============================================================
# 程序入口
# ============================================================

def main():

    try:

        app = SecurityDemoUI()

        app.run()

    except Exception as error:

        log(
            f"程序启动失败：{error}"
        )

        import traceback

        traceback.print_exc()


# ============================================================
# 启动
# ============================================================

if __name__ == "__main__":

    main()
