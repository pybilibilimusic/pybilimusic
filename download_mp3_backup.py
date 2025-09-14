import time
import logging
from pathlib import Path
import urllib3
import requests
import re
import subprocess
from generate_w_rid_and_wts import generate_wrid

# 添加请求头，模拟浏览器行为
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.bilibili.com' # Referer是必须的
    }

def get_video_id(bilibili_url):
    pattern = r"(?:BV|av|AV)[0-9A-Za-z]{10,}"

    match = re.search(pattern, bilibili_url)
    return match.group(0)

def get_video_aid_and_cid(video_id):
    api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={video_id}"
    json_data = requests.get(api_url, headers=headers,verify=False).json()
    aid = json_data['data']['aid']
    pic = json_data['data']['pic']
    title = json_data['data']['title']
    cid = json_data['data']['cid']
    return aid,pic,title,cid

def get_mp3(aid,cid,title):
    params = {"aid": aid, "cid": cid}
    w_rid, wts = generate_wrid(params)
    get_video_link = f"https://api.bilibili.com/x/player/wbi/playurl?avid={aid}&cid={cid}&qn=16&type=mp4&platform=html5&fnver=0&fnval=16&aid={aid}&web_location=1315877&w_rid={w_rid}&wts={wts}".format(aid=aid, cid=cid, w_rid=w_rid, wts=wts)
    response = requests.get(get_video_link, headers=headers, verify=False).json()
    video_url = response['data']['durl'][0]['url']
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    video_name = re.sub(r'[<>:"/\\|?*《》]', '', title)
    logging.info(f"经处理后的文件名：{video_name},开始下载视频")
    video_path = temp_dir / f"{video_name}.mp4"
    mp3_path = temp_dir / f"{video_name}.mp3"
    response = requests.get(video_url, stream=True,headers=headers,verify=False)
    with open(video_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logging.info(f"视频{video_name}下载完成！")
    logging.info(f"视频{video_name}开始转换为MP3")
    # 使用ffmpeg转换
    result = subprocess.run([
        'ffmpeg', '-i', str(video_path),
        '-q:a', '0', '-map', 'a',
        str(mp3_path), '-y'
    ],  capture_output=True, text=True, check=True)
    if result.stderr:
        logging.info(f"FFmpeg完整输出:\n{result.stderr}")
    logging.info(f"视频{video_name}转换完成！")

def main(url):
    log_dir = Path("./log")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "{}.log".format(str(time.time()))
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename=log_path)
    video_id = get_video_id(url)
    logging.info(f"获取视频AV/BV号：{video_id}")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    aid, pic, title, cid = get_video_aid_and_cid(video_id)
    logging.info(f"获取视频的aid：{aid},cid:{cid},标题：{title},封面地址：{pic}")
    get_mp3(aid, cid, title)

if __name__ == '__main__':
    url = input()
    main(url = url)
