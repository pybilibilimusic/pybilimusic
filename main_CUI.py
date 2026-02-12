import configparser
import os
from pathlib import Path
import time

import requests

import config
import song_search
import download_mp4
import select_file
import sys
import logging

import transform


class main_CUI:
    def __init__(self):
        self.video_prefix = "https://www.bilibili.com/video/"
        self.config_path = Path("config.ini")
        self.config = configparser.ConfigParser()
        self.search = song_search.Song_Search()
        self.downloader = download_mp4.download_mp4()

    def clear_screen(self):
        if os.name == 'nt':  # Windows 系统
            os.system('cls')

        else:  # Linux 或 macOS 系统
            os.system('clear')

    def downloading(self,video_id,video_title,video_path):
        """Download video from Bilibili and save to specified path.

        Args:
            video_id (str): The AV or BV ID of the video
            video_title (str): The title of the video, used as file name
            video_path (Path): The save path for the downloaded video file

        Returns:
            None

        Raises:
            None
        """
        print("Downloading video'{0}'，please wait……".format(video_title))
        video_url = self.video_prefix+video_id
        self.downloader.download_video(video_url)
        print(f"Video '{video_title}' download complete!Saved to'{video_path}'")

    def set_logging(self):
        config.logging_path.mkdir(exist_ok=True)
        log_path = config.logging_path / "{}.log".format(str(time.time()))
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S",
                            filename=log_path)

    # def main():
    #     """The main function,which achieve the downloading of the designated video
    #     and the convertion of this video."""
    #
    #     set_logging()
    #
    #     video_id, video_title = choose_id()
    #
    #
    #     temp_dir.mkdir(exist_ok=True)
    #
    #     video_path = temp_dir / f"{video_title}.mp4"
    #     mp3_path = temp_dir / f"{video_title}.mp3"
    #
    #     downloading(video_id, video_title,video_path)
    #
    #     #Transform(video_path,mp3_path),用法已改！！！

    def batch_processing(self):
        # 修改1：使用不同的变量名避免冲突
        print("Please select a txt file in the window:")
        txt_path = select_file.select_file()

        # 修改2：添加错误检查
        if not txt_path:
            print("File selection cancelled.")
            return

        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                context = f.read()
        except FileNotFoundError:
            print(f"File not found: {txt_path}")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return

        # 修改3：过滤空行
        song_list = [line.strip() for line in context.split("\n") if line.strip()]

        # 修改4：添加进度反馈
        total_songs = len(song_list)
        print(f"Found {total_songs} songs to process.")

        for index, name in enumerate(song_list, 1):
            try:
                print(f"\nProcessing {index}/{total_songs}: {name}")

                # 修改5：使用不同的变量名
                video_id, video_title = self.search.filter_video(name)

                print(f"Video starts downloading: {video_title}")

                # 修改7：假设 video_prefix 是类的属性
                video_url = self.video_prefix + video_id
                self.downloader.download_video(bilibili_url=video_url)

                print(f"Download completed for: {video_title}")

            except Exception as e:
                print(f"Error processing '{name}': {e}")
                continue  # 继续处理下一首歌曲

        print("\nBatch processing completed!")

    def program_menu(self):
        print("="*50)
        print("Menu Options:")
        print("Search and download the specified video → Please enter 1")
        print("Download specific video and convert it to MP3 → Please enter 2")
        print("Download a single video only by entering the url → Please enter 3")
        print("Download a single video and convert it to MP3 → Please enter 4")
        print("Batch download videos (supports txt files) → Please enter 5")
        print("Transform MP4 files to MP3 → Please enter 6")
        print("Exit the program → Please enter 7")
        print("="*50)

    def download_by_name(self):
        prompt = input("Please enter the song name:")
        video_id, video_title = self.search.filter_video(prompt=prompt, timeout=3)
        video_title = config.normalize_filename(video_title)
        print(f"Video downloading soon: {video_title}")
        video_url = self.video_prefix + video_id
        self.downloader.download_video(video_url)
        return video_title

    def download_by_url(self):
        bilibili_url = input("Please paste the url here:")
        response = requests.get(bilibili_url, headers = config.headers, timeout = 5, stream = True)
        response.raise_for_status()
        print("The entered link has been verified as valid, starting the download.")
        video_title = self.downloader.download_video(bilibili_url=bilibili_url)
        video_title = config.normalize_filename(video_title)
        print("Download completed successfully!")
        return video_title


    def self_check(self):
        """Download video from Bilibili and save to specified path."""
        try:
            if os.path.exists(self.config_path):
                self.config.read(self.config_path)
                first_run = self.config.get('first_run', 'first_run')
                if first_run == '1':
                    # 初始化已全部完成
                    return True
                else:
                    print("初始化被用户意外中断，重新开始……")
                    return True  # initial_setup()
            else:
                pass  # initial_setup
                # return True

        except KeyboardInterrupt:
            sys.exit("The user has exited the program……")

        except Exception:
            print(f"Unknown error: {Exception}, please contact the developer to resolve it...")

    def main(self):
        try:
            os.system("chcp 65001 >nul")
            self.clear_screen()
            self.self_check()
            while True:
                self.program_menu()
                user_choice = input("Please choose (1-7): ")
                if user_choice == "1":
                    self.download_by_name()
                elif user_choice == "2":
                    video_title = self.download_by_name()
                    transform.transform(config.temp_dir+video_title)
                elif user_choice == "3":
                    self.download_by_url()
                elif user_choice == "4":
                    transform
                elif user_choice == "5":
                    sys.exit("We look forward to your next visit.")
                else:
                    print("Invalid input, please try again.")
                self.clear_screen()

        except KeyboardInterrupt:
            sys.exit("The user has exited the program……")

        except requests.exceptions.ConnectionError:
            print("Network connection failed, please check your network.")

        except requests.exceptions.Timeout:
            print("The request has timed out, and the download has been automatically interrupted.")

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error code: {e.response.status_code}")

        except requests.exceptions.MissingSchema:
            print("URL format error:missing protocol header")

        except requests.exceptions.InvalidURL:
            print("Invalid URL")

        except requests.exceptions.InvalidSchema:
            print("Unsupported protocol")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

        except PermissionError:
            print("You do not have permission to write to the file.")

        except OSError as e:
            print(f"File system error: {e}")

        except Exception:
            print(f"Unknown error: {Exception}, please contact the developer to resolve it...")

if __name__ == "__main__":
    main()    
