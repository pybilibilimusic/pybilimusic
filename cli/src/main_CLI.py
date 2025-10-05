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
    
def choose_id():
    """Get user input for song name and search for matching videos。"""
    prompt = input("Please enter the name of the song you want to download (case-sensitive):")
    print("Please wait a moment, searching...")
    encoded_prompt = requests.utils.quote(prompt)  # URL encode the search query
    video_title, video_id = song_search.search(encoded_prompt)

    # Find the best result (avoid "循环" and "纯享" versions)
    best_index = 0
    for i in range(5):
        current_title = video_title[i]
        print(str(i+1)+"."+current_title)
    for i in range(5):
        current_title = video_title[i]
        if "循环" not in current_title and "纯享" not in current_title:
            best_index = i
            break 
    
    print("Please enter a number to make a selection. If no selection is made, the optimal result will be automatically chosen after 10 seconds...")
    print(f"The best result is: {best_index + 1}.{video_title[best_index]}")

    user_choice = -1
    start_time = time.time()
    
    sys.stdout.write("Please choose (1-5): ")
    sys.stdout.flush()
    
    # Wait for user input with 10-second timeout
    while time.time() - start_time < 10:
        if sys.platform == "win32":
        #Windows platform input handling
            try:
                import msvcrt
                if msvcrt.kbhit():
                    user_input = input()
                    try:
                        user_choice = int(user_input)
                        if 1 <= user_choice <= 5:
                            break
                        else:
                            print("Invalid input, please enter a number between 1 and 5.")
                            sys.stdout.write("Please choose (1-5):")
                            sys.stdout.flush()
                    except ValueError:
                        print("The input is not a valid number, please enter it again.")
                        sys.stdout.write("Please choose (1-5): ")
                        sys.stdout.flush()
            except ImportError:
                time.sleep(1)
        else:
            # Unix/Linux platform input handling
            if select.select([sys.stdin], [], [], 1)[0]:
                user_input = sys.stdin.readline().strip()
                try:
                    user_choice = int(user_input)
                    if 1 <= user_choice <= 5:
                        break
                    else:
                        print("Please enter a number between 1 and 5")
                        sys.stdout.write("Please choose (1-5): ")
                        sys.stdout.flush()
                except ValueError:
                    print("The input is not a valid number, please enter it again.")
                    sys.stdout.write("Please choose (1-5): ")
                    sys.stdout.flush()
                    
        # Update remaining time display
        remaining = 10 - int(time.time() - start_time)
        sys.stdout.write(f"\rRemaining time: {remaining} seconds | Please choose (1-5): ")
        sys.stdout.flush()
    
    print()
    
    # Determine final selection
    if 1 <= user_choice <= 5:
        final_choice = user_choice - 1
        print(f"已选择: {user_choice}.{video_title[final_choice]}")
    else:
        final_choice = best_index
        print(f"Timeout, automatically select the optimal result: {best_index + 1}.{video_title[best_index]}")
    
    return video_id[final_choice],video_title[final_choice]

def downloading(video_id,video_title,video_path):
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
    print("Downloading video'{0}'，please wait^……".format(video_title))
    video_url = "https://www.bilibili.com/video/"+video_id
    download_mp4.main(video_url)
    print(f"Video '{video_title}' download complete!Saved to'{video_path}'")

def transform(video_path,mp3_path):
    """Convert video file to MP3 audio file using FFmpeg.
    
    Args:
    video_path (Path): The save path for the downloaded video file
    mp3_path (Path): The save path for the converted mp3 file
    
    Returns:
        None
        
    Raises:
        None
    """
    logging.info(f"Video {video_path} start converting to MP3")
    result = subprocess.run([
        'ffmpeg', '-i', str(video_path),
        '-q:a', '0', '-map', 'a',
        str(mp3_path), '-y'
    ],  capture_output=True, text=True, encoding='utf-8', errors='ignore', check=True)
    if result.stderr:
        logging.info(f"The complete output of FFmpeg:\n{result.stderr}")
    logging.info(f"Video {video_path} conversion completed!")
    print(f"Video {video_path} onversion completed!")

def main():
    """The main function,which achieve the downloading of the designated video
    and the convertion of this video."""
    log_dir = Path("./log")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "{}.log".format(str(time.time()))
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename=log_path)
    
    video_id, video_title = choose_id()
    
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    
    video_path = temp_dir / f"{video_title}.mp4"
    mp3_path = temp_dir / f"{video_title}.mp3"
    
    downloading(video_id, video_title,video_path)
       
    transform(video_path,mp3_path)        
        
if __name__ == "__main__":
    main()    
