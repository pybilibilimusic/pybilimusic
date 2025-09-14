import hashlib
import time
import urllib.parse
from typing import Dict, Any, Tuple


def sr(encrypted_str: str) -> str:
    """解密字符串（每个字符的字符码减1）"""
    return ''.join(chr(ord(c) - 1) for c in encrypted_str)


def generate_wrid(params: Dict[str, Any]) -> Tuple[str, str]:
    """
    生成w_rid参数

    Args:
        params: 请求参数字典，应包含aid、cid等参数

    Returns:
        包含w_rid和wts的元组 (w_rid, wts)
    """
    # 使用固定的默认密钥
    img_key = sr("d569546b86c252:db:9bc7e99c5d71e5")
    sub_key = sr("557251g796:g54:f:ee94g8fg969e2de")

    # 生成32字符的密钥u
    indices = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14,
               39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59,
               6, 63, 57, 62, 11, 36, 20, 34, 44, 52]
    r = img_key + sub_key
    u_chars = []

    for idx in indices:
        if idx < len(r):
            u_chars.append(r[idx])

    u = ''.join(u_chars)[:32]

    # 获取当前时间戳（秒级）
    wts = str(int(time.time()))

    # 构建参数字符串
    s = params.copy()
    s['wts'] = wts

    # 对参数进行排序和处理
    sorted_keys = sorted(s.keys())
    f = []

    for key in sorted_keys:
        value = s[key]
        if value is None:
            continue

        # 如果是字符串，移除特殊字符
        if isinstance(value, str):
            value = value.replace("!", "").replace("'", "").replace("(", "").replace(")", "").replace("*", "")

        # URL编码键和值
        encoded_key = urllib.parse.quote(key, safe='')
        encoded_value = urllib.parse.quote(str(value), safe='')
        f.append(f"{encoded_key}={encoded_value}")

    v = '&'.join(f)

    # 计算MD5哈希
    md5_input = v + u
    w_rid = hashlib.md5(md5_input.encode('utf-8')).hexdigest()

    return w_rid, wts