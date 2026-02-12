import webbrowser
import subprocess
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from pathlib import Path

import config
import downloading
from select_file import select_file

class Transform:
    def __init__(self):
        self.temp_path = Path("./temp")
        self.default_installation_path = [
            r"C:\Program Files\7-Zip\7z.exe",
            r"C:\Program Files (x86)\7-Zip\7z.exe"
        ]
        self.ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/"

    def check_if_ffmpeg_exists(self):
        try:
            subprocess.check_output([r'.\ffmpeg', '-version'])
            flag = True
        except FileNotFoundError:
            while True:
                user_choice = input("ffmpeg is not installed,do you want to download automatically?(enter y/n)")
                if user_choice.lower() == 'y':
                    print("please waiting,downloading ffmpeg zip...")
                    flag = True
                    break
                elif user_choice.lower() == 'n':
                    print("please install ffmpeg.exe into this folder.")
                    flag = False
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
        return flag


    def check_7zip_exists(self):
        exe_path = None
        for path in self.default_installation_path:
            if os.path.exists(path):
                exe_path = path
                break
        if not exe_path:
            print("7-zip is not in the default installation path.")
            while True:
                user_choice = input('Do you need to open the 7-zip official website to download the 7-zip manually?(y/n)')
                if user_choice.lower() == 'y':
                    webbrowser.open("https://www.7-zip.org/")
                    print("Please press enter to continue after you install the 7-zip manually...")
                    input("Press enter to continue...")
                    break
                elif user_choice.lower() == 'n':
                    print("Please install 7-zip manually and run this program again...")
                    sys.exit()
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
            while True:
                exe_path = input("Please enter 7-zip installation path: ")
                if os.path.exists(Path(exe_path) / "7z.exe"):
                    break
                else:
                    print("Invalid input. Please input the correct 7-zip installation path.")
            return exe_path
        else:
            return exe_path


    def install_ffmpeg(self):
        response = requests.get(url=self.ffmpeg_url, headers=config.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        ffmpeg_zip_element = soup.select_one(
            '#article-content > section:nth-child(2) > div.section-body > div:nth-child(1) > code:nth-child(2) > a:nth-child(1)')
        pattern = r'href="([^"]*)"'
        ffmpeg_zip_url = re.search(pattern, str(ffmpeg_zip_element))
        downloading.download(ffmpeg_zip_url.group(1))
        path = Path(".")
        archive_path = list(path.glob("ffmpeg-*-essentials_build.7z"))[0]
        exe_path = self.check_7zip_exists()
        try:
            cmd = [exe_path, "e", archive_path, f"-o{path}", "*/bin/ffmpeg.exe", "-r", "-y"]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during decompression:{e.stderr}")
            sys.exit(1)
        print("ffmpeg is installed successfully.")

    def transform(self,file_path,target_suffix = "mp3"):
        filename = Path(file_path).stem
        target_path = self.temp_path / f"{filename}.{target_suffix}"
        result = subprocess.run([
            'ffmpeg', '-i', str(file_path),
            '-q:a', '0', '-map', 'a',
            str(target_path), '-y'],
            capture_output=True, text=True, encoding='utf-8',
            errors='ignore', check=True)
        return result


if __name__ == "__main__":
    try:
        transform = Transform()
        flag = transform.check_if_ffmpeg_exists()
        if not flag:
            transform.install_ffmpeg()
        file_path = select_file(title = "请选择需转换的文件:",
                                filetypes = [("Video File",config.video_suffix),
                                             ("Audio File",config.audio_suffix)])
        # 执行转换
        transform.transform(file_path,target_suffix = ".mp3")
    except subprocess.CalledProcessError:
        sys.exit("用户取消了选择，自动退出程序……")
    except Exception as e:
        print(e)