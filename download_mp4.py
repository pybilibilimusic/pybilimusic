import urllib3
import requests
import re
from generate_params import generate_wrid
import downloading
import config

class download_mp4:
    def __init__(self):
        self.api_url = f"https://api.bilibili.com/x/web-interface/view?bvid="
        self.pattern = r"(?:BV|av|AV)[0-9A-Za-z]{10,}"

    def get_video_id(self,bilibili_url):
        """Extract AV or BV string from bilibili link using regular expressions.

        Args:
            bilibili_url (str) :The bilibili url to be extracted

        Returns:
            The AV or BV string in bilibili link.

        Raises:
            None
        """

        match = re.search(self.pattern, bilibili_url)
        return match.group(0)

    def get_video_information(self,video_id):
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
        api_url = self.api_url + video_id
        json_data = requests.get(api_url, headers=config.headers,verify=False).json()
        aid = json_data['data']['aid']
        pic = json_data['data']['pic']
        title = json_data['data']['title']
        cid = json_data['data']['cid']
        return aid,pic,title,cid

    def get_mp4(self,aid,cid,title):
        """?????
        Get some specific args.

        Args:
            aid (str) :The specific args of this video.
            cid (str) :The specific args of this video.
            title (str) :The title of this video,will be used as file name.

        Returns:
            None
        Raises:
            None
        """
        params = {"aid": aid, "cid": cid}
        w_rid, wts = generate_wrid(params)
        get_video_link = f"https://api.bilibili.com/x/player/wbi/playurl?avid={aid}&cid={cid}&qn=16&type=mp4&platform=html5&fnver=0&fnval=16&aid={aid}&web_location=1315877&w_rid={w_rid}&wts={wts}".format(aid=aid, cid=cid, w_rid=w_rid, wts=wts)
        response = requests.get(get_video_link, headers=config.headers, verify=False).json()
        response.raise_for_status()
        video_url = response['data']['durl'][0]['url']
        video_name = config.normalize_filename(filename = title)
    #    logging.info(f"经处理后的文件名：{video_name},开始下载视频")

        downloading.download(video_url,f"{video_name}.mp4")
    #    logging.info(f"视频{video_name}下载完成！")

    def download_video(self,bilibili_url):
        """The main function,which achieve the downloading of the designated video
        Args:
            bilibili_url (str) :The bilibili url.

        Returns:
            None

        Raises:
            None
        """
        # log_dir = Path("./log")
        # log_dir.mkdir(exist_ok=True)
        # log_path = log_dir / "{}.log".format(str(time.time()))
        # logging.basicConfig(level=logging.INFO,
        #                     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        #                     datefmt="%Y-%m-%d %H:%M:%S",
        #                     filename=log_path)
        video_id = self.get_video_id(bilibili_url)
        #logging.info(f"获取视频AV/BV号：{video_id}")
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        aid, pic, title, cid = self.get_video_information(video_id)
        #logging.info(f"获取视频的aid：{aid},cid:{cid},标题：{title},封面地址：{pic}")
        #temp_dir = Path("./temp")
        #temp_dir.mkdir(exist_ok=True)
        self.get_mp4(aid, cid, title)
        return title

if __name__ == '__main__':
    """The test code"""
    url = input("请输入Bilibili视频链接:")
    downloader = download_mp4()
    downloader.download_video(bilibili_url=url)
