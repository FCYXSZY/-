from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep


def getDataFromWeb(url, nowTime, proxy):
    try:
        # 浏览器配置
        browser_options = Options()
        #browser_options.add_argument('--headless')  # 如果你需要无头模式
        browser_options.add_argument('--disable-gpu')
        browser_options.add_argument("--proxy-server=" + proxy)

        # 使用 webdriver-manager 自动下载和管理 ChromeDriver
        service = Service(ChromeDriverManager().install())  # 安装并启动 ChromeDriver
        browser = webdriver.Chrome(service=service, options=browser_options)

        browser.get(url)
        #browser.switch_to_frame('x-URS-iframe')  # 需先跳转到iframe框架
        print(url)
        sleep(2)
        #print(browser.page_source)
        taget = [a.text for a in browser.find_elements(By.CLASS_NAME, 'gtm-new-work-tag-event-click')]
        print(taget)
        temp = [b.text for b in [a.find_element(By.TAG_NAME, 'dd') for a in
                                 browser.find_element(By.CLASS_NAME, 'dpDffd').find_elements(By.TAG_NAME, 'li')]]
        print(temp)
        writer = browser.find_element(By.CLASS_NAME, 'fATptn').find_element(By.TAG_NAME, 'div').text
        print(writer)
        browser.quit()  # 退出浏览器

        return [nowTime, writer, temp[0], temp[1], temp[2], taget]
        # rank = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item[data-rank="1"]').get_attribute('data-rank')
        # title = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item[data-rank="1"]').get_attribute('data-title')
        # user_name = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item[data-rank="1"]').get_attribute(
        #     'data-user-name')
        # date = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item[data-rank="1"]').get_attribute('data-date')
        # view_count = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item[data-rank="1"]').get_attribute(
        #     'data-view-count')
        # rating_count = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item[data-rank="1"]').get_attribute(
        #     'data-rating-count')
        # image_url = browser.find_element(By.CSS_SELECTOR,
        #                                  'section.ranking-item[data-rank="1"] .ranking-image-item img').get_attribute(
        #     'data-src')
        #
        # # 使用显示等待确保元素加载完成
        # data_list = []
        # rank = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item').get_attribute('data-rank')
        # title = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item').get_attribute('data-title')
        # user_name = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item').get_attribute('data-user-name')
        # date = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item').get_attribute('data-date')
        # view_count = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item').get_attribute('data-view-count')
        # rating_count = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item').get_attribute('data-rating-count')
        # image_url = browser.find_element(By.CSS_SELECTOR, 'section.ranking-item .ranking-image-item img').get_attribute(
        #     'data-src')
        # # 打印提取的信息
        # print("Rank:", rank)
        # print("Title:", title)
        # print("User:", user_name)
        # print("Date:", date)
        # print("View Count:", view_count)
        # print("Rating Count:", rating_count)
        # print("Image URL:", image_url)
        #     data_list.append([date, user_name, title, view_count, rating_count, image_url])
        #
        #
        #     return data_list
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return []



url = 'https://www.pixiv.net/artworks/124818547'
nowTime = '2024-12-02 00:00'
proxy = 'http://127.0.0.1:7890'
data = getDataFromWeb(url, nowTime, proxy)
print(data)
