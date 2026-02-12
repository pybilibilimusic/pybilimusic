import re
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

char_map = {
    '——': '--',  # 中文破折号 → 两个连字符
    '―': '-',  # 长破折号 → 短横线
    '—': '-',  # em dash → 短横线
    '：': ':',  # 全角冒号 → 半角
    '；': ';',  # 全角分号 → 半角
    '，': ',',  # 全角逗号 → 半角
    '。': '.',  # 全角句号 → 半角
    '！': '!',  # 全角感叹号 → 半角
    '？': '?',  # 全角问号 → 半角
    '（': '(',  # 全角左括号 → 半角
    '）': ')',  # 全角右括号 → 半角
    '【': '[',  # 全角左方括号 → 半角
    '】': ']',  # 全角右方括号 → 半角
    '《': '<',  # 左书名号 → 小于号
    '》': '>',  # 右书名号 → 大于号
    '·': '.',  # 中点 → 句点
    '‧': '.',  # 连字点 → 句点
    '「': '[',  # 左引号
    '」': ']',  # 右引号
    '『': '[',  # 左双引号
    '』': ']',  # 右双引号
    '﹑': ',',  # 顿点 → 逗号
    '﹔': ';',  # 全角分号 → 半角
    '﹕': ':',  # 全角冒号 → 半角
    '﹖': '?',  # 全角问号 → 半角
    '﹗': '!',  # 全角感叹号 → 半角
    '＂': '"',  # 全角双引号 → 半角
    '＇': "'",  # 全角单引号 → 半角
    '＼': r'\\',  # 全角反斜杠 → 半角
    '＃': '#',  # 全角井号 → 半角
    '＄': '$',  # 全角美元符 → 半角
    '％': '%',  # 全角百分号 → 半角
    '＆': '&',  # 全角and符 → 半角
    '＊': '*',  # 全角星号 → 半角
    '＋': '+',  # 全角加号 → 半角
    '－': '-',  # 全角减号 → 半角
    '／': '/',  # 全角斜杠 → 半角
    '＜': '<',  # 全角小于号 → 半角
    '＝': '=',  # 全角等号 → 半角
    '＞': '>',  # 全角大于号 → 半角
    '＠': '@',  # 全角at符 → 半角
    '＾': '^',  # 全角异或符 → 半角
    '＿': '_',  # 全角下划线 → 半角
    '｀': '`',  # 全角反引号 → 半角
    '｛': '{',  # 全角左花括号 → 半角
    '｜': '|',  # 全角竖线 → 半角
    '｝': '}',  # 全角右花括号 → 半角
    '～': '~',  # 全角波浪号 → 半角
    '｟': '(',  # 全角左括号
    '｠': ')',  # 全角右括号
    '｡': '.',  # 全角句点
    '｢': '[',  # 全角左方括号
    '｣': ']',  # 全角右方括号
    '､': ',',  # 全角逗号
    '･': '.',  # 全角中点
    '￣': '_',  # 上划线
    '￤': '|',  # 全角竖线
    # 特殊空格字符
    '\u200B': '',  # 零宽空格
    '\uFEFF': '',  # 零宽不中断空格
    '\u00A0': ' ',  # 不间断空格 → 普通空格
    '\u2000': ' ',  # en空格
    '\u2001': ' ',  # em空格
    '\u2002': ' ',  # en空格
    '\u2003': ' ',  # em空格
    '\u2004': ' ',  # 三分之一em空格
    '\u2005': ' ',  # 四分之一em空格
    '\u2006': ' ',  # 六分之一em空格
    '\u2007': ' ',  # 数字空格
    '\u2008': ' ',  # 标点空格
    '\u2009': ' ',  # 瘦空格
    '\u200A': ' ',  # 头发空格
    '\u202F': ' ',  # 窄不中断空格
    '\u205F': ' ',  # 中等数学空格
    '\u3000': ' ',  # 全角空格 → 半角空格
}

windows_illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'

video_suffix = [
    '.mp4',   # 最可靠
    '.mkv',   # 非常可靠
    '.avi',   # 很可靠
    '.mov',   # 很可靠
    '.wmv',   # Windows可靠
    '.flv',   # Flash
    '.webm',  # WebM
    '.mpg',   # MPEG
    '.mpeg',  # MPEG
    '.m4v',   # Apple
    '.3gp',   # 手机
]

# 可直接转换的音频格式
audio_suffix = [
    '.mp3',   # 标准
    '.wav',   # 原始
    '.flac',  # 无损
    '.aac',   # AAC
    '.m4a',   # Apple AAC
    '.ogg',   # Ogg Vorbis
    '.opus',  # Opus
    '.wma',   # Windows（Windows系统上）
]

temp_dir = Path("./temp")
logging_path = Path("./log")

def normalize_filename(filename):
    for old_char, new_char in char_map.items():
        filename = filename.replace(old_char, new_char)
    filename = re.sub(windows_illegal_chars, "_",filename)
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip(' _.')
    return filename