# -*- coding: utf-8 -*-
"""
网络安全演练 UI Demo
仅用于课堂演示 / UI 开发 / 安全意识培训

特点：
- 全屏窗口
- 居中白色演练面板
- 红色边框
- 左上演练徽章
- 右上状态信息框
- 中间蓝红渐变视觉区域
- 演练编号
- 模拟金额
- 模拟锁定提示
- 72 小时演示倒计时
- 不包含真实支付功能
- 不包含真实政府机构身份冒充
- ESC 可安全退出
- Ctrl+Shift+Q 连续 3 次也可退出
"""

import tkinter as tk
from tkinter import messagebox
import time
import random
import string
from datetime import datetime, timedelta


# ============================================================
# 基础配置
# ============================================================

WINDOW_BG = "#050505"

PANEL_WIDTH = 825
PANEL_HEIGHT = 590

RED = "#ff1111"
DARK_RED = "#b30000"
BLUE = "#1010e8"
WHITE = "#ffffff"
BLACK = "#000000"
GRAY = "#d5d5d5"
DARK_GRAY = "#777777"
GREEN = "#008f00"


# ============================================================
# 工具
# ============================================================

def generate_demo_id():
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(10))


def log(msg):
    print(
        f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
        f"{msg}"
    )


# ============================================================
# 主界面
# ============================================================

class SecurityDemoUI:

    def __init__(self):
        self.root = tk.Tk()

        self.root.title("网络安全演练")

        self.root.configure(
            bg=WINDOW_BG
        )

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight()

            self.root.geometry(
                f"{w}x{h}+0+0"
            )

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # 演练编号
        self.demo_id = generate_demo_id()

        # 模拟倒计时
        self.countdown_end = (
            datetime.now() + timedelta(hours=72)
        )

        # 快捷键退出计数
        self.exit_count = 0
        self.last_exit_press = 0

        log("Security Demo UI 启动")
        log(f"演练编号: {self.demo_id}")

        self.build_ui()

        self.update_countdown()

        # 安全退出
        self.root.bind(
            "<Escape>",
            self.safe_exit
        )

        self.root.bind(
            "<Control-Shift-Q>",
            self.exit_press
        )

        self.root.bind(
            "<Control-Shift-q>",
            self.exit_press
        )

    # ========================================================
    # 主界面
    # ========================================================

    def build_ui(self):

        # ====================================================
        # 背景
        # ====================================================

        background = tk.Frame(
            self.root,
            bg=WINDOW_BG
        )

        background.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # 中央面板
        # ====================================================

        panel_x = (
            self.screen_width - PANEL_WIDTH
        ) // 2

        panel_y = (
            self.screen_height - PANEL_HEIGHT
        ) // 2

        self.panel = tk.Frame(
            self.root,
            bg=WHITE,
            highlightbackground=RED,
            highlightthickness=5
        )

        self.panel.place(
            x=panel_x,
            y=panel_y,
            width=PANEL_WIDTH,
            height=PANEL_HEIGHT
        )

        # ====================================================
        # 顶部区域
        # ====================================================

        top = tk.Frame(
            self.panel,
            bg=WHITE
        )

        top.place(
            x=10,
            y=10,
            width=PANEL_WIDTH - 20,
            height=160
        )

        # ====================================================
        # 左上演练徽章
        # ====================================================

        self.create_demo_badge(
            top
        )

        # ====================================================
        # 右上状态框
        # ====================================================

        self.create_status_box(
            top
        )

        # ====================================================
        # 中央主体
        # ====================================================

        body = tk.Frame(
            self.panel,
            bg=WHITE
        )

        body.place(
            x=10,
            y=165,
            width=PANEL_WIDTH - 20,
            height=410
        )

        # ====================================================
        # 演练警告条
        # ====================================================

        self.create_warning_banner(
            body
        )

        # ====================================================
        # 标题区域
        # ====================================================

        self.create_title(
            body
        )

        # ====================================================
        # 说明文字
        # ====================================================

        self.create_description(
            body
        )

        # ====================================================
        # 演练按钮
        # ====================================================

        self.create_button(
            body
        )

        # ====================================================
        # 底部重要提示
        # ====================================================

        self.create_notice(
            body
        )

        # ====================================================
        # 左下角演练编号
        # ====================================================

        tk.Label(
            self.root,
            text=(
                f"SECURITY TRAINING DEMO    "
                f"ID: {self.demo_id}"
            ),
            font=(
                "Consolas",
                8
            ),
            fg="#777777",
            bg=WINDOW_BG
        ).place(
            x=10,
            y=self.screen_height - 25
        )

    # ========================================================
    # 演练徽章
    # ========================================================

    def create_demo_badge(self, parent):

        canvas = tk.Canvas(
            parent,
            width=145,
            height=145,
            bg=WHITE,
            highlightthickness=0
        )

        canvas.place(
            x=5,
            y=5
        )

        # 外圈
        canvas.create_oval(
            5,
            5,
            140,
            140,
            fill="#e9e9e9",
            outline="#bbbbbb",
            width=2
        )

        # 红色圆
        canvas.create_oval(
            17,
            17,
            128,
            128,
            fill="#d71920",
            outline="#a40000",
            width=3
        )

        # 五角星
        self.draw_star(
            canvas,
            72,
            48,
            22,
            "#ffd900"
        )

        # 四角星
        for x, y in [
            (43, 66),
            (102, 66),
            (51, 92),
            (93, 93)
        ]:
            self.draw_star(
                canvas,
                x,
                y,
                9,
                "#ffd900"
            )

        # 中心文字
        canvas.create_text(
            72,
            108,
            text="安全演练",
            font=(
                "Microsoft YaHei",
                13,
                "bold"
            ),
            fill="#ffd900"
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

        import math

        points = []

        for i in range(10):

            angle = (
                math.pi / 2
                + i * math.pi / 5
            )

            r = (
                radius
                if i % 2 == 0
                else radius * 0.42
            )

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

        box = tk.Frame(
            parent,
            bg=GRAY,
            relief="solid",
            bd=1
        )

        box.place(
            x=540,
            y=10,
            width=270,
            height=127
        )

        rows = [
            ("您的状态：", "演练中", GREEN),
            ("当前设备：", "已连接", GREEN),
            ("当前会话：", "安全演示", GREEN),
            ("演练地址：", "127.0.0.1", "#000000"),
            ("测试文件：", "仅模拟锁定", DARK_RED),
        ]

        for i, (
            label,
            value,
            color
        ) in enumerate(rows):

            tk.Label(
                box,
                text=label,
                font=(
                    "Microsoft YaHei",
                    11
                ),
                bg=GRAY,
                fg="#111111",
                anchor="w"
            ).place(
                x=7,
                y=7 + i * 22,
                width=92
            )

            tk.Label(
                box,
                text=value,
                font=(
                    "Microsoft YaHei",
                    11,
                    "bold"
                ),
                bg=GRAY,
                fg=color,
                anchor="w"
            ).place(
                x=98,
                y=7 + i * 22,
                width=155
            )

    # ========================================================
    # 警告 Banner
    # ========================================================

    def create_warning_banner(self, parent):

        shadow = tk.Label(
            parent,
            text="你的电脑已被锁定！",
            font=(
                "Microsoft YaHei",
                22,
                "bold"
            ),
            fg="#3333ff",
            bg="#c8c8ff"
        )

        shadow.place(
            x=17,
            y=12,
            width=300,
            height=84
        )

        # 红蓝主背景
        banner = tk.Canvas(
            parent,
            width=300,
            height=84,
            highlightthickness=0,
            bg=WHITE
        )

        banner.place(
            x=10,
            y=5
        )

        # 外发光层
        for i in range(5, 0, -1):

            banner.create_rectangle(
                i,
                i,
                300 - i,
                84 - i,
                fill="#eeeeff",
                outline="#6666ff",
                width=1
            )

        # 左红区域
        banner.create_rectangle(
            4,
            4,
            156,
            80,
            fill="#d6003d",
            outline=""
        )

        # 右蓝区域
        banner.create_rectangle(
            156,
            4,
            296,
            80,
            fill="#0707dc",
            outline=""
        )

        banner.create_text(
            150,
            42,
            text="你的电脑已被锁定！",
            font=(
                "Microsoft YaHei",
                20,
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
            text=f"演练编号：{self.demo_id}",
            font=(
                "Microsoft YaHei",
                20,
                "bold"
            ),
            fg="#006000",
            bg=WHITE
        ).place(
            x=335,
            y=13
        )

        tk.Label(
            parent,
            text="模拟事件",
            font=(
                "Microsoft YaHei",
                26,
                "bold"
            ),
            fg=BLACK,
            bg=WHITE
        ).place(
            x=335,
            y=48
        )

        tk.Label(
            parent,
            text="800元",
            font=(
                "Microsoft YaHei",
                24,
                "bold"
            ),
            fg=DARK_RED,
            bg=WHITE
        ).place(
            x=545,
            y=49
        )

    # ========================================================
    # 描述
    # ========================================================

    def create_description(self, parent):

        text = (
            "本页面为网络安全课堂演练界面，用于模拟终端遭遇恶意锁定后的视觉效果。\n"
            "页面中的编号、金额、设备状态及倒计时均为虚构数据，不代表真实事件。\n"
            "\n"
            "演练目的：帮助学习者识别仿冒执法机构、虚假罚款和勒索页面等社会工程学攻击。\n"
            "请勿向任何陌生页面提供银行卡、验证码、密码或转账信息。"
        )

        tk.Label(
            parent,
            text=text,
            font=(
                "Microsoft YaHei",
                11
            ),
            fg="#111111",
            bg=WHITE,
            justify="left",
            anchor="nw",
            wraplength=755
        ).place(
            x=12,
            y=112,
            width=770,
            height=112
        )

    # ========================================================
    # 按钮
    # ========================================================

    def create_button(self, parent):

        button = tk.Button(
            parent,
            text="查看演练说明",
            font=(
                "Microsoft YaHei",
                14,
                "bold"
            ),
            fg=WHITE,
            bg="#9c0000",
            activeforeground=WHITE,
            activebackground="#d00000",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.show_demo_info
        )

        button.place(
            x=310,
            y=225,
            width=205,
            height=58
        )

        # 阴影
        shadow = tk.Frame(
            parent,
            bg="#dddddd"
        )

        shadow.place(
            x=305,
            y=230,
            width=205,
            height=58
        )

        button.lift()

    # ========================================================
    # 说明
    # ========================================================

    def create_notice(self, parent):

        notice = (
            "重要提示！\n"
            "这是网络安全培训模拟页面，不是真实公安机关通知，也不涉及任何真实罚款。\n"
            "页面不会删除文件，不会上传个人信息，也不会进行任何真实支付操作。\n"
            "退出演练：按 ESC，或连续按 Ctrl + Shift + Q 三次。"
        )

        tk.Label(
            parent,
            text=notice,
            font=(
                "Microsoft YaHei",
                10
            ),
            fg=DARK_RED,
            bg=WHITE,
            justify="center"
        ).place(
            x=20,
            y=305,
            width=765,
            height=95
        )

        # 倒计时
        tk.Label(
            parent,
            text="演练计时：",
            font=(
                "Microsoft YaHei",
                12,
                "bold"
            ),
            fg=BLACK,
            bg=WHITE
        ).place(
            x=315,
            y=380
        )

        self.countdown_label = tk.Label(
            parent,
            text="72:00:00",
            font=(
                "Consolas",
                16,
                "bold"
            ),
            fg=DARK_RED,
            bg=WHITE
        )

        self.countdown_label.place(
            x=405,
            y=377
        )

    # ========================================================
    # 演练说明
    # ========================================================

    def show_demo_info(self):

        messagebox.showinfo(
            "网络安全演练",
            (
                "这是一个纯 UI 演示。\n\n"
                "编号："
                + self.demo_id
                + "\n\n"
                "所有状态均为虚构数据。\n"
                "不会进行真实支付。\n"
                "不会删除文件。\n"
                "不会上传数据。"
            ),
            parent=self.root
        )

    # ========================================================
    # 倒计时
    # ========================================================

    def update_countdown(self):

        remain = (
            self.countdown_end
            - datetime.now()
        )

        seconds = int(
            remain.total_seconds()
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

        minutes, secs = divmod(
            remainder,
            60
        )

        self.countdown_label.config(
            text=(
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{secs:02d}"
            )
        )

        self.root.after(
            1000,
            self.update_countdown
        )

    # ========================================================
    # ESC
    # ========================================================

    def safe_exit(self, event=None):

        log("ESC 安全退出")

        self.root.destroy()

    # ========================================================
    # Ctrl + Shift + Q
    # ========================================================

    def exit_press(self, event=None):

        now = time.time()

        if now - self.last_exit_press > 2:
            self.exit_count = 0

        self.last_exit_press = now

        self.exit_count += 1

        log(
            f"退出快捷键："
            f"{self.exit_count}/3"
        )

        if self.exit_count >= 3:

            self.root.destroy()

    # ========================================================
    # 运行
    # ========================================================

    def run(self):

        self.root.mainloop()


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":

    try:

        app = SecurityDemoUI()

        app.run()

    except Exception as e:

        print(
            "[ERROR]",
            e
        )