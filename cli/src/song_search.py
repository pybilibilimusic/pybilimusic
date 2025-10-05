from bs4 import BeautifulSoup
import requests
import re
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.bilibili.com'  # Referer是必须的
}
def search(prompt):
    search_url = f'https://search.bilibili.com/all?keyword={prompt}'
    response = requests.get(url = search_url,headers=headers)
    search_html = BeautifulSoup(response.text,'html.parser')
    search_list = str(search_html.find_all('div', class_='bili-video-card__info--right'))
    video_id_pattern = r'href="//www\.bilibili\.com/video/([^/]+)/'
    title_pattern = r'title="(.*?)">'
    video_title = re.findall(title_pattern, search_list)
    video_id = re.findall(video_id_pattern, search_list)
    final_video_title = video_title[0:5]
    final_video_id = video_id[0:5]
    return final_video_title,final_video_id

if __name__ == "__main__":
    prompt = "past lives"
    encoded_prompt = requests.utils.quote(prompt)
    song_search(encoded_prompt)
