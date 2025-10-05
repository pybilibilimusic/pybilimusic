from pathlib import Path
from bs4 import BeautifulSoup
import requests
import re
import os
import time
import song_search
import download_mp4
import threading
import select
import sys
import logging
import subprocess

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
def choose_id():
    prompt = input("请输入需下载的歌曲名称(区分大小写)：")
    print("请稍等，正在搜索……")
    encoded_prompt = requests.utils.quote(prompt)
    video_title, video_id = song_search.search(encoded_prompt)
    
    best_index = 0
    for i in range(5):
        current_title = video_title[i]
        print(str(i+1)+"."+current_title)
    for i in range(5):
        current_title = video_title[i]
        if "循环" not in current_title and "纯享" not in current_title:
            best_index = i
            break 
    
    print("请输入数字进行选择，如不选择，将在10秒后自动选择最优结果……")
    print(f"最优结果: {best_index + 1}.{video_title[best_index]}")

    # 使用非阻塞输入实现超时
    user_choice = -1
    start_time = time.time()
    
    # 显示初始提示
    sys.stdout.write("请选择(1-5): ")
    sys.stdout.flush()
    
    while time.time() - start_time < 10:
        # 检查是否有输入可用
        if sys.platform == "win32":
            # Windows平台
            try:
                import msvcrt
                if msvcrt.kbhit():
                    user_input = input()
                    try:
                        user_choice = int(user_input)
                        if 1 <= user_choice <= 5:
                            break
                        else:
                            print("请输入1-5之间的数字")
                            sys.stdout.write("请选择(1-5): ")
                            sys.stdout.flush()
                    except ValueError:
                        print("输入的不是有效数字，请重新输入")
                        sys.stdout.write("请选择(1-5): ")
                        sys.stdout.flush()
            except ImportError:
                # 如果没有msvcrt，使用简单等待
                time.sleep(1)
        else:
            # Unix/Linux平台
            if select.select([sys.stdin], [], [], 1)[0]:
                user_input = sys.stdin.readline().strip()
                try:
                    user_choice = int(user_input)
                    if 1 <= user_choice <= 5:
                        break
                    else:
                        print("请输入1-5之间的数字")
                        sys.stdout.write("请选择(1-5): ")
                        sys.stdout.flush()
                except ValueError:
                    print("输入的不是有效数字，请重新输入")
                    sys.stdout.write("请选择(1-5): ")
                    sys.stdout.flush()
        
        # 显示剩余时间（在同一行更新）
        remaining = 10 - int(time.time() - start_time)
        sys.stdout.write(f"\r剩余时间: {remaining}秒 | 请选择(1-5): ")
        sys.stdout.flush()
    
    print()  # 换行
    
    # 处理最终选择
    if 1 <= user_choice <= 5:
        final_choice = user_choice - 1
        print(f"已选择: {user_choice}.{video_title[final_choice]}")
    else:
        final_choice = best_index
        print(f"超时，自动选择最优结果: {best_index + 1}.{video_title[best_index]}")
    
    return video_id[final_choice],video_title[final_choice]

def downloading(video_id,video_title,video_path):
    print("正在下载视频'{0}'，请稍候……".format(video_title))
    video_url = "https://www.bilibili.com/video/"+video_id
    download_mp4.main(video_url)
    print(f"视频'{video_title}'下载完成！已保存至'{video_path}'")

def transform(video_path,mp3_path):
    logging.info(f"视频{video_path}开始转换为MP3")
    # 使用ffmpeg转换
    result = subprocess.run([
        'ffmpeg', '-i', str(video_path),
        '-q:a', '0', '-map', 'a',
        str(mp3_path), '-y'
    ],  capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
    if result.stderr:
        logging.info(f"FFmpeg完整输出:\n{result.stderr}")
    logging.info(f"视频{video_path}转换完成！")
    print(f"视频{video_path}转换完成！")

def main():
    log_dir = Path("./log")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "{}.log".format(str(time.time()))
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename=log_path)
    # 首先获取视频ID和标题
    video_id, video_title = choose_id()
    
    # 然后创建临时目录
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    
    # 定义文件路径
    video_path = temp_dir / f"{video_title}.mp4"
    mp3_path = temp_dir / f"{video_title}.mp3"
    
    # 下载视频
    downloading(video_id, video_title,video_path)
    
    # 转换视频为MP3    
    transform(video_path,mp3_path)        
        
if __name__ == "__main__":
    main()    
