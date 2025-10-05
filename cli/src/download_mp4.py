import os
import time
import logging
from pathlib import Path
import urllib3
import requests
import re
from generate_w_rid_and_wts import generate_wrid
from rich.progress import (
        Progress, BarColumn, DownloadColumn, TextColumn, 
        TimeRemainingColumn, TransferSpeedColumn
    )

# Add request headers to simulate browser behavior.
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.bilibili.com' # Referer is required
    }

def download_with_rich(video_url, video_path):
    response = requests.get(video_url, stream=True, headers=headers, verify=False)
    total_size = int(response.headers.get('content-length', 0))
    
    # Custom progress bar class,using basic characters.
    class SimpleBarColumn(BarColumn):
        def render(self, task):
            """Render the progress bar using basic ASCII characters."""
            bar = ""
            width = int(self.bar_width * task.percentage / 100)
            if width > 0:
                bar = "=" * (width - 1) + ">"
            if width < self.bar_width:
                bar += " " * (self.bar_width - width)
            return bar
    
    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        SimpleBarColumn(bar_width=50),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )
    
    with progress:
        task = progress.add_task(
            "下载",
            filename=os.path.basename(video_path),
            total=total_size
        )
        
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
                    
def get_video_id(bilibili_url):
    """Extract AV or BV string from bilibili link using regular expressions.
    
    Args:
        bilibili_url (str) :The bilibili url to be extracted
        
    Returns:
        The AV or BV string in bilibili link.
        
    Raises:
        None
    """
    pattern = r"(?:BV|av|AV)[0-9A-Za-z]{10,}"

    match = re.search(pattern, bilibili_url)
    return match.group(0)

def get_video_information(video_id):
    """Get some specific args.
    
    Args:
        video_id (str) :The bilibili url.
        
    Returns:
        aid,cid (str) :The specific args of this video.
        title (str) :The title of this video.
        pic (str) :The cover of this video.
    Raises:
        None
    """
    api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={video_id}"
    json_data = requests.get(api_url, headers=headers,verify=False).json()
    aid = json_data['data']['aid']
    pic = json_data['data']['pic']
    title = json_data['data']['title']
    cid = json_data['data']['cid']
    return aid,pic,title,cid

def get_mp4(aid,cid,title,video_path):
    """Get some specific args.

    Args:
        aid (str) :The specific args of this video.
        cid (str) :The specific args of this video.
        title (str) :The title of this video,will be used as file name.
        video_path (str) :The temp saving path of the video.

    Returns:
        None
    Raises:
        None
    """
    params = {"aid": aid, "cid": cid}
    w_rid, wts = generate_wrid(params)
    get_video_link = f"https://api.bilibili.com/x/player/wbi/playurl?avid={aid}&cid={cid}&qn=16&type=mp4&platform=html5&fnver=0&fnval=16&aid={aid}&web_location=1315877&w_rid={w_rid}&wts={wts}".format(aid=aid, cid=cid, w_rid=w_rid, wts=wts)
    response = requests.get(get_video_link, headers=headers, verify=False).json()
    video_url = response['data']['durl'][0]['url']
    video_name = re.sub(r'[<>:"/\\|?*《》]', '', title)
    logging.info(f"经处理后的文件名：{video_name},开始下载视频")
        
    download_with_rich(video_url, video_path)
    logging.info(f"视频{video_name}下载完成！")

def main(url):
    """The main function,which achieve the downloading of the designated video
    Args:
        url (str) :The bilibili url.

    Returns:
        None

    Raises:
        None
    """
    if os.name == 'nt':  # Windows系统
        os.system('chcp 65001 >nul')  # 设置控制台编码为UTF-8
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
    aid, pic, title, cid = get_video_information(video_id)
    logging.info(f"获取视频的aid：{aid},cid:{cid},标题：{title},封面地址：{pic}")
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    video_path = temp_dir / f"{title}.mp4"
    get_mp4(aid, cid, title,video_path)

if __name__ == '__main__':
    """The test code"""
    url = input()
    main(url = url)
