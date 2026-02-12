import sys
import time

import select
from bs4 import BeautifulSoup
import requests
import re
import config

class Song_Search:
    def __init__(self):
        self.keyword_url = 'https://search.bilibili.com/all?keyword='
        self.video_id_pattern = r'href="//www\.bilibili\.com/video/([^/]+)/'
        self.title_pattern = r'title="(.*?)">'
        self.blacklist_word = ["纯享","循环"]

    def search(self,prompt):
        search_url = self.keyword_url + prompt
        response = requests.get(url = search_url,headers=config.headers)
        search_html = BeautifulSoup(response.text,'html.parser')
        search_list = str(search_html.find_all('div', class_='bili-video-card__info--right'))
        video_title = re.findall(self.title_pattern, search_list)
        video_id = re.findall(self.video_id_pattern, search_list)
        final_video_title = video_title[0:5]
        final_video_id = video_id[0:5]
        return final_video_title,final_video_id

    def filter_video(self, prompt,timeout=10):
        """Get user input for song name and search for matching videos。"""
        print("Please wait a moment, searching...")
        encoded_prompt = requests.utils.quote(prompt)  # URL encode the search query
        video_title, video_id = self.search(encoded_prompt)
        # Find the best result (avoid "循环" and "纯享" versions)
        best_index = 0

        for i in range(5):
            current_title = video_title[i]
            print(str(i + 1) + "." + current_title)
            if self.blacklist_word not in current_title:
                best_index = i
                break

        print(f"Please enter a number to make a selection. If no selection is made, the optimal result will be automatically chosen after {timeout} seconds...")
        print(f"The best result is: {best_index + 1}.{video_title[best_index]}")

        user_choice = -1
        start_time = time.time()

        sys.stdout.write("Please choose (1-5): ")
        sys.stdout.flush()

        # Wait for user input with certain timeout
        while time.time() - start_time < timeout:
            if sys.platform == "win32":
                # Windows platform input handling
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
            remaining = timeout - int(time.time() - start_time)
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

        return video_id[final_choice], video_title[final_choice]

if __name__ == "__main__":
    prompt = input("Test code only:please enter the video title you want to search for:")
    song_search = Song_Search()
    video_title,video_id = song_search.filter_video(prompt,timeout=3)
    print(video_title)
    print(video_id)