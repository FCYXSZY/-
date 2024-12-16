import os
import requests
import re
from time import sleep
from tqdm import tqdm
from configparser import RawConfigParser
from typing import Dict

import dataclasses

# 读取配置文件
config = RawConfigParser()
config.read(r"D:\py大作业\pixiv-\flask2\config\config.ini", encoding="utf-8")

# 获取配置
savePath = config.get("reptile", "savePath")
Cookie = config.get("reptile", "Cookie")
UA = config.get("reptile", "UA")
# proxy = config.get("reptile", "proxy")

# 代理配置（确保代理服务器已运行）
@dataclasses.dataclass  # 使用 dataclass 装饰器
class ProxyConfig:
    proxy: Dict = dataclasses.field(default_factory=lambda: {"https": "http://127.0.0.1:7890"})

# 初始化代理配置
proxy_config = ProxyConfig()

# 请求头
headers = {
    "Cookie": "first_visit_datetime_pc=2023-12-09%2021%3A31%3A13; p_ab_id=0; p_ab_id_2=6; p_ab_d_id=244589072; yuid_b=NlCVUYk; privacy_policy_notification=0; a_type=0; b_type=0; login_ever=yes; device_token=8356e6c1013cc6294b3a3f7956959538; privacy_policy_agreement=7; c_type=20; _im_vid=01JE3ADR0ZXFNSQ376V4P2MDPF; _gcl_au=1.1.1144295421.1733131284; __cf_bm=MwvJ45b..KemUK1MKnA0pKJlqTT48hESbEMe0HNjUgE-1733293411-1.0.1.1-UrvOF6m3m5u6_ocIf8HGlxQUqofhBz90YkVhFCFmAOAahtcNn61NqylTyDn2JDeG9tIAbFZ_hNRojKpTeimCgR7PcDAcybOHB50wAuYBwNo; cf_clearance=1CiGGORvOKrXpakkPYXKzpVU_A7E40TAfLI_H_yN01Q-1733293412-1.2.1.1-sBmM5duXrswtnhN4W9KILH2SMcKSoYSOI2v5GVaHh5rLKxS.3V8Os7rSP7u2WXP2K9UkLEIoldI6plTv80anM5nOfKGp.jApfw29B8xdwAxTvVbavFSja3VLprNDqMxTfXd6Zjr2xNoHcPjx7F7yihKEYbtVspFz2JwocsmrDSWONwlY9Xo4dxY.fkGcCO4iKE_8mrQa.lexYjUme3rV1Si6fprt7NMBqfVWrf91.gtyeRUjlqz8bdP1i6TYXH0y1pSETrBaMbbK09MadrHtFlnkxdTGeySVbeaySJp1uNQEVNSTZ5W1akFcLqNRN98x9ApT3oiGGowS0jnT3LVQPofJ1t92UsPFI0EgBPWnaMouFQOPQ1ImTwCYVip811dtIbxLxZ6HcMEnVmqINdjYqw; PHPSESSID=49934750_NGntZmQyGNe8yYtMJPmxxdffyf3EwPc0; _ga_MZ1NL4PHH0=GS1.1.1733293419.8.1.1733293441.0.0.0; _gid=GA1.2.1918966557.1733293445; _gat_UA-1830249-3=1; _ga_75BBYNYN9J=GS1.1.1733293414.12.1.1733293463.0.0.0; _ga=GA1.2.565933053.1702125080",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}

def get_format(url):
    match = re.search(r'\.(\w+)$', url)
    if match:
        image_format = match.group(1)
        print(image_format)  # 输出：png
        return image_format
    else:
        print("无法提取图片格式")
        return "jpg"
def download_image(url):
    """
    下载图片并保存到指定目录
    """
    print(savePath)
    save_dir = savePath  # 图片保存路径
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)  # 如果文件夹不存在，则创建

    try:
        result = re.search(r"/(\d+)_", url)
        image_id = result.group(1)
        image_name = url[url.rfind("/") + 1:]  # 获取文件名
        header = {"Referer": f"https://www.pixiv.net/artworks/{image_id}"}
        headers.update(header)  # 更新请求头
        print(f"https://www.pixiv.net/artworks/{image_id}")
        #formatd=get_format(url)
        print(f"downloading {image_name}")
        save_path = os.path.join(save_dir, f"{image_name}")  # 图片保存路径
        proxy = None  # 或者不传递 proxies 参数
        # 请求并下载图片
        response = requests.get(url, headers=headers, proxies=proxy_config.proxy)
        sleep(0.5)
        if response.status_code == 200:
            #wb 只写方式打开或新建一个二进制文件，只允许写数据。
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):  # 分块写入文件
                    f.write(chunk)
            print(f"Image saved: {save_path}")
        else:
            print(f"Failed to download image: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")

def download_images(image_urls):
    """
    批量下载图片，传入图片 URL 列表
    """
    # 使用 tqdm 展示下载进度
    for image_url in tqdm(image_urls, desc="Downloading images", ncols=100, unit="images"):
        download_image(image_url)
        sleep(1)


if __name__ == "__main__":
    # 示例：下载图片
    image_urls = [
        'https://i.pximg.net/img-original/img/2024/12/08/08/00/06/124996182_p0.jpg',  # 填入图片的URL
        'https://i.pximg.net/img-original/img/2024/12/10/00/00/21/125049816_p0.png'  # 填入图片的URL
    ]
    download_images(image_urls)  # 批量下载图片
