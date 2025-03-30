import asyncio
import json

# from multiprocessing import Pool, cpu_count
from multiprocessing import Queue
import os
import random
import sys
from threading import Lock
import threading
import traceback
from types import CoroutineType
from typing import List

import aiofiles
import httpx
import requests

# 添加 Douyin_TikTok_Download_API
current_dir = os.path.dirname(os.path.abspath(__file__))
a_dir = os.path.abspath(os.path.join(current_dir, "Douyin_TikTok_Download_API"))
sys.path.append(a_dir)


import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from Douyin_TikTok_Download_API.crawlers.hybrid.hybrid_crawler import HybridCrawler


def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    # 试验
    options.add_argument("--disable-infobars")
    # options.add_argument("start-maximized") #  最大化
    options.add_argument("--disable-extensions")
    # Pass the argument 1 to allow and 2 to block
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 1}
    )

    # 尝试绕开 Google安全，以登录google账号
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    return options


options = get_default_chrome_options()
options.binary_location = "chrome-linux64/chrome"
service = webdriver.ChromeService(executable_path="chromedriver-linux64/chromedriver")
driver = webdriver.Chrome(service=service, options=options)


# 使用 Python3.13.2的 无GIL版本自由线程, 容器自带锁，因此无需额外加锁
# 从页面获取原始视频分享链接队列
global_raw_share_urls_queue = []
# 解析后的视频下载链接队列
queue_lock = Lock()
global_parsed_video_urls_queue = []
# 去重
global_url_sets = set([])


def download_video(url, caption, headers: dict = None, file_path: str = None):
    headers = (
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if headers is None
        else headers.get("headers")
    )
    for i in range(1):
        try:
            if str(caption).startswith("."):
                # 跳过 .开头
                continue
            if len(str(caption).strip().replace(".", "").strip()) == 0:
                # 跳过空文本视频
                print("skip empty caption video")
                continue
            caption = str(caption).replace("*", "")

            print(f"Downloading video : {caption}")
            caption = str(caption).replace("\n", "")
            if os.path.exists(file_path):
                print(f"Video {file_path} already exists, skipping...")
                continue

            response = requests.get(url, headers=headers)
            with open(file_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading video  {e}")


async def download_single_url(url_desc_tag: tuple[str, str, str]):
    try:
        no_watermark_video_url = url_desc_tag[0]

        description = url_desc_tag[1]
        tag = url_desc_tag[2]

        file_path = os.path.abspath(
            os.path.join("downloads_tiktok", tag, description + ".mp4")
        )
        if os.path.exists(file_path):
            print(f"已存在, 跳过: {no_watermark_video_url}")
            return
        __headers = await HybridCrawler().TikTokWebCrawler.get_tiktok_headers()
        download_video(
            url=no_watermark_video_url,
            caption=description,
            headers=__headers,
            file_path=file_path,
        )
        print(f"下载成功: {file_path}")
    except Exception as e:
        print("error: ", e)


async def parse_tiktok_share_urls(share_urls: List[str], tag: str):
    """解析"""
    # 开始解析数据
    ret_data = []
    for url in share_urls:
        try:
            data = await HybridCrawler().hybrid_parsing_single_video(
                url=url, minimal=True
            )
            no_watermark_video_url = data.get("video_data").get("nwm_video_url_HQ")
            description = data.get("desc").strip()
            if len(description) > 200:
                description = str(description.strip())[:200]
            description = description.replace("/", "_")

            global_parsed_video_urls_queue.append(
                (no_watermark_video_url, description, tag)
            )
        except Exception as e:
            print("hybrid_parsing_single_video 报错: ", e)
            # return
    return ret_data


def download_url_wrapper():
    while True:
        if queue_lock.acquire() and len(global_parsed_video_urls_queue) > 0:
        #if queue_lock.acquire() and len(global_parsed_video_urls_queue) > 0:
            url_desc_tag = global_parsed_video_urls_queue.pop(0)

            # 立即释放锁
            queue_lock.release()
            try:
                asyncio.run(
                    download_single_url(
                        url_desc_tag,
                    )
                )
            except Exception as e:
                print(e)
        time.sleep(1)


# 获取页面内容
async def get_page_video_share_urls(url, tag: str):
    driver.get(url)
    start_time = time.time()

    await asyncio.sleep(15)
    # 使用 set去重
    ret_videos = set()
    # 获取初始滚动高度
    last_height = driver.execute_script("return document.body.scrollHeight")
    while time.time() - start_time < 5 * 60 * 60:
        r = get_video_share_url()
        try:
            print("scrolling...")
            # 滚到到底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 向下滚动一页
            # driver.execute_script("window.scrollBy(0, window.innerHeight);")
        except Exception as e:
            print(f"Error scrolling: {e}")
            continue

        if len(r) > 0:
            ret_videos.update(r)
            tmp_start = time.time()

            await parse_tiktok_share_urls(r, tag)
            # download_tiktok_urls(url_descs_tag)
            print("==================")
            print(r)
            print("==================")
            # while time.time() - tmp_start < 20:
                # await asyncio.sleep(1)
        else:
            await asyncio.sleep(10)

        # 休眠几秒，等待页面加载
        try_times = 0
        new_height = 0
        while try_times < 10:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(15)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    await asyncio.sleep(3)
                else:
                    break
            except Exception as e:
                print(f"Error scrolling: {e}")
            finally:
                try_times += 1

        if try_times == 10 and new_height == last_height:
            print("滚动到底部了，已经滚不动了")
            break

        last_height = new_height
        pass

    # return ret_videos
    # time.sleep(1200)
    return []


def get_video_share_url():
    """
    获取页面中的视频和文案
    """
    videos = []

    # 等待页面加载完成后查找视频
    print("get_video_and_text_ex")
    vidoe_div_list = driver.find_elements(
        By.CLASS_NAME, "css-x6y88p-DivItemContainerV2"
    )
    print("vidoe_list length:", len(vidoe_div_list))

    for video_div in vidoe_div_list:
        try:
            link = video_div.find_element(By.TAG_NAME, "a")
            video_share_url = link.get_attribute("href")
            if video_share_url not in global_url_sets:
                videos.append(video_share_url)

                # 加入全局
                # global_raw_share_urls_queue.append(video_share_url)
                global_url_sets.add(video_share_url)
        except NoSuchElementException as e:
            print("video标签不存在: " + str(e))
        except Exception as e:
            print(f"Error extracting video or caption: {e}")
    return videos


def login_tiktok():
    driver.get("https://www.tiktok.com/tag/meme")
    time.sleep(10000)
    pass


async def main():
    # share_url = "https://www.tiktok.com/@g1885068req/video/7483013990390582583?is_from_webapp=1&sender_device=pc"
    # share_url = "https://www.tiktok.com/@notnayelig/video/7477658217661877550?is_from_webapp=1&sender_device=pc"
    # await download_tiktok(share_url)

    # login_tiktok()

    # download_video(
    #     url="https://v16m-default.akamaized.net/e6fa9d80e2e6454538eac706609a858e/67e6df2f/video/tos/useast2a/tos-useast2a-ve-0068-euttp/oQk5uBrERE0ARPdf6DIQ2fDlYQQFEDCEBQrSR5/?a=0&bti=OHYpOTY0Zik3OjlmOm01MzE6ZDQ0MDo%3D&ch=0&cr=13&dr=0&er=0&lr=all&net=0&cd=0%7C0%7C0%7C&cv=1&br=1498&bt=749&cs=2&ds=6&ft=XE5bCqx4m3lPD12U~z9J3wU682StMeF~O5&mime_type=video_mp4&qs=11&rc=aDVnNjk7Njs0Njw5NTw7Z0BpM2h5OXc5cjM3cTMzZjczM0AuMS0wLmAwXzAxM2MvLzIwYSM1Z29hMmRrNmZgLS1kMWNzcw%3D%3D&vvpl=1&l=202503281140450ABFE7BF0EFF8F3CC646&btag=e000b8000",
    #     caption="xxx",
    #     headers=None,
    #     file_path="xxx.mp4",
    # )
    # return

    pages = [
        # "https://www.tiktok.com/tag/meme",
        # "https://www.tiktok.com/tag/funny",
        # "https://www.tiktok.com/tag/food",
        "https://www.tiktok.com/tag/dancing",
        "https://www.tiktok.com/tag/dance",
        "https://www.tiktok.com/tag/eating",
        "https://www.tiktok.com/tag/fyp",
        "https://www.tiktok.com/tag/foryou",
        "https://www.tiktok.com/tag/foryoupage",
        "https://www.tiktok.com/tag/funnyvideos",
        "https://www.tiktok.com/tag/fy",
        "https://www.tiktok.com/tag/prank",
        "https://www.tiktok.com/tag/fun",
        "https://www.tiktok.com/tag/pets",
        "https://www.tiktok.com/tag/anime",
        "https://www.tiktok.com/tag/beauty",
        "https://www.tiktok.com/tag/basketball",
        "https://www.tiktok.com/tag/blackpink",
        "https://www.tiktok.com/tag/cute",
        "https://www.tiktok.com/tag/capcut",
        "https://www.tiktok.com/tag/comedia",
        "https://www.tiktok.com/tag/duet",
        "https://www.tiktok.com/tag/explore",
        "https://www.tiktok.com/tag/game",
        "https://www.tiktok.com/tag/humor",
        "https://www.tiktok.com/tag/happy",
        "https://www.tiktok.com/tag/kpop",
        "https://www.tiktok.com/tag/makeup",
        "https://www.tiktok.com/tag/music",
        "https://www.tiktok.com/tag/love",
        "https://www.tiktok.com/tag/like",
        "https://www.tiktok.com/tag/new",
    ]




    for i in range(os.cpu_count() - 2):
        threading.Thread(
            target=download_url_wrapper,
        )

    for url in pages:
        try:
            tag = url.replace("https://www.tiktok.com/tag/", "").strip()
            if not os.path.exists(os.path.join("downloads_tiktok", tag)):
                os.makedirs(os.path.join("downloads_tiktok", tag), exist_ok=True)
            await get_page_video_share_urls(url, tag)
        except Exception as e:
            print(f"Error getting videos from {url}: {e}")
            traceback.print_exc()
    pass


if __name__ == "__main__":
    asyncio.run(main())
