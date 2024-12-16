import requests
import pandas as pd
from lxml import etree
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from time import sleep
import threading
import DAO
from pyecharts import options as opts
from pyecharts.charts import Map, Timeline, Bar, Line, Pie, EffectScatter
from pyecharts.charts import WordCloud
import configparser
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
import re
import os
import download
import json
# 读取配置文件
config = configparser.RawConfigParser()
config.read(r"D:\py大作业\pixiv-\flask2\config\config.ini")

Cookie = config.get("reptile", "Cookie")
UA = config.get("reptile", "UA")
proxy = config.get("reptile", "proxy")
driverUrl = config.get("reptile", "driverUrl")
savePath = config.get("reptile", "savePath")
download_num = int(config.get("reptile", "download_num"))

up_url = "https://www.pixiv.net"
headers = {
    "Cookie": Cookie,
    "User-Agent": UA
}

mainurl = "https://www.pixiv.net/ranking.php"
# 数据列表
data_list = []
browser = None
download_list=[]
# 获取动态页面数据
# 注意需要爬取的信息是会改变的如fATptn的作者位置，需要去亲自去网页确认
def ret_match(master_image_url):
    match = re.search(r"/img-master/img/(.+?)_p\d+", master_image_url)  # 更正后的正则表达式
    if match:
        extracted_part = match.group(1)
        return extracted_part
    else:
        return None
def extract_and_build_pixiv_url(match):
    #从未登录状态获取原图的链接，暴力拼接法
    """从 master 图片 URL 提取信息并构建 original 图片 URL。"""
    if match:
        extracted_part = match
        possible_url = []
        original_image_url1 = f"https://i.pximg.net/img-original/img/{extracted_part}_p0.jpg"  # 添加 _p0
        original_image_url2 = f"https://i.pximg.net/img-original/img/{extracted_part}_p0.png"
        possible_url.extend([original_image_url1, original_image_url2])
        return possible_url
    else:
        return None

def getDataFromWeb(url, nowTime):
    global browser, download_num
    browser.get(url)
    taget = [a.text for a in browser.find_elements(By.CLASS_NAME,'gtm-new-work-tag-event-click')]

    temp = [b.text for b in [a.find_element(By.TAG_NAME,'dd') for a in
                             browser.find_element(By.CLASS_NAME,'dpDffd').find_elements(By.TAG_NAME,'li')]]

    writer = browser.find_element(By.CLASS_NAME,'fATptn').find_element(By.TAG_NAME,'div').text
    imgurl = ''
    if download_num > 0:
        try:
            image_element = browser.find_element(By.CSS_SELECTOR, "img.sc-1qpw8k9-1")
            # parent_a_element = image_element.find_element(By.XPATH, "..")
            # image_url = parent_a_element.get_attribute("href")
            image_url = image_element.get_attribute("src")
            url_match=ret_match(image_url)
            original_image_url = extract_and_build_pixiv_url(url_match)
            imgurl = url_match
            # original_image_url= [image_url]
            # imgurl = image_url
            print(f"Image URL: {imgurl}")
            if(download_num==1): pass
            else:
                download_list.extend(original_image_url)
                download_num -= 1

        except Exception as e:
            print('不许看哦')
            pass
            #print(f"Error while downloading image: {e}")

    return [nowTime, writer, temp[0], temp[1], temp[2], taget, imgurl]

# 线程任务—获取数据
def thread_getData(url_list,nowTime):
    for url in tqdm(url_list, desc="获取数据进度", ncols=100, unit="项"):  # 使用 tqdm 包装 url_list
        print('--'+url)
        data_list.append(getDataFromWeb(url,nowTime))

# 获取下一页的数据
def get_NewPage(url):
    if url == "":
        url = "https://www.pixiv.net/ranking.php?mode=daily&content=illust"
    print(url)
    context = requests.get(url = url,headers=headers,proxies={'http':'http://127.0.0.1:7890','https':'http://127.0.0.1:7890','socks':'socks5://127.0.0.1:7890'}).text
    html = etree.HTML(context)
    print('finished get')
    nowtime = html.xpath('//*[@id="wrapper"]/div[1]/div/div[2]/div/nav[2]/ul/li[2]/a/text()')[0] # 获取当前排名的日期----nowtime
    print(nowtime.encode("utf-8").decode("utf-8"))
    o = html.xpath('/html/body/div[3]/div[1]/div/div[3]/div[1]/section/div[2]/a[1]/@href')
    o = [up_url+x for x in o if "user" not in x] # 各个图片的网页
    return o,nowtime,html

# 获取Cookie并加载到Selenium中
def getCookie(driver):
    driver.get("https://www.pixiv.net/")
    time.sleep(60)
    print(driver.get_cookies())
    with open('cookies.txt', 'w') as f:
        f.write(json.dumps(driver.get_cookies()))
def login(driver):
    driver.get("https://www.pixiv.net/")
    with open('cookies.txt', 'r') as f:
        cookies_list = json.load(f)
        for cookie in cookies_list:
            # 检查并转换Cookie中的expiry字段
            if isinstance(cookie.get('expiry'), float):
                cookie['expiry'] = int(cookie['expiry'])
            driver.add_cookie(cookie)
    driver.refresh()



if __name__ == "__main__":


    # cookie_list = []
    # for cookie_str in Cookie.split(';'):
    #     cookie = {}
    #     name, value = cookie_str.strip().split('=', 1)
    #     cookie['name'] = name
    #     cookie['value'] = value
    #     cookie_list.append(cookie)
    # print(cookie_list)
    # 进入各个网页，收集他们的标签等信息
    browser_options = Options()
    browser_options.add_argument('--headless')
    browser_options.add_argument('--disable-gpu')
    browser_options.add_argument("--proxy-server=" + proxy)

    # browser_options.add_argument("--proxy-server=http://10.112.78.231:7890")
    service = Service(driverUrl)
    browser = webdriver.Edge(service=service, options=browser_options)

    # browser.get('https://www.pixiv.net')  # 先访问Pixiv首页以触发Cookie加载
    # load_cookies_to_browser(browser, cookie_list)
    #getCookie(browser)
    #login(browser)
    # browser.refresh()
    #pass
    start = time.time()
    threads = []
    next_url = ""
    ok = False
    for j in range(1):
        o, nowtime, html = get_NewPage(next_url)
        l = 0
        r = len(o) // 5
        thread_getData(o,nowtime)
        #for i in range(10):
        #    thread1 = threading.Thread(target=thread_getData, args=(o[l:r], nowtime))
        #    l += len(o) // 5
        #    r += len(o) // 5
        #    threads.append(thread1)
        #for i in threads:
        #    i.start()
        #for t in threads:
        #    t.join()

        print("ok!", end=" ")
        #print(nowtime)
        print(len(data_list))

        print("\n")
        # for t in threads:
        #     del (t)
        # threads.clear()
        if ok == False:
            next_url = \
            [mainurl + i for i in html.xpath('//*[@id="wrapper"]/div[1]/div/div[2]/div/nav[2]/ul/li[3]/a/@href')][0]
            ok = True
        else:
            next_url = \
            [mainurl + i for i in html.xpath('//*[@id="wrapper"]/div[1]/div/div[2]/div/nav[2]/ul/li[4]/a/@href')][0]
    end = time.time()
    print(end - start)
    browser.close()
    browser.quit()
    data = pd.DataFrame(data_list)
    #print(data)

    #最后再下载图片
    print(download_list)
    download.download_images(download_list)

    data.columns = ['日期', '作者', '点赞', '收藏', '浏览', '类型', '图片url']
    data['点赞'] = data['点赞'].str.replace(',', '')
    data[['点赞']] = data[['点赞']].astype('int')
    data['收藏'] = data['收藏'].str.replace(',', '')
    data[['收藏']] = data[['收藏']].astype('int')
    data['浏览'] = data['浏览'].str.replace(',', '')
    data[['浏览']] = data[['浏览']].astype('int')
    data['日期'] = data['日期'].astype('string')
    data['作者'] = data['作者'].astype('string')
    data['类型'] = data['类型'].astype('string')
    data['评分'] = data.点赞 * 0.3 + data.收藏 * 0.5 + data.浏览 * 0.2
    data['图片url'] = data['图片url'].astype('string')
    DAO.insert(data)