import asyncio
import json
from multiprocessing import Pool, cpu_count
import os
import random
import sys
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

# from crawlers.hybrid.hybrid_crawler import HybridCrawler
from Douyin_TikTok_Download_API.crawlers.hybrid.hybrid_crawler import HybridCrawler


import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


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


url_sets = set([])


async def fetch_data(url: str, headers: dict = None):
    headers = (
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if headers is None
        else headers.get("headers")
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # 确保响应是成功的
        return response


# 下载视频专用
# async def fetch_data_stream(url: str, headers: dict = None, file_path: str = None):
#     headers = (
#         {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }
#         if headers is None
#         else headers.get("headers")
#     )
#     async with httpx.AsyncClient() as client:
#         # 启用流式请求
#         print(f"流式下载url: {url}")
#         async with client.stream("GET", url, headers=headers) as response:
#             response.raise_for_status()

#             # 流式保存文件
#             async with aiofiles.open(file_path, "wb") as out_file:
#                 async for chunk in response.aiter_bytes():
#                     # if await request.is_disconnected():
#                     #     print("客户端断开连接，清理未完成的文件")
#                     #     await out_file.close()
#                     #     os.remove(file_path)
#                     #     return False
#                     await out_file.write(chunk)
#             return True


def download_video(url_desc, headers: dict = None, file_path: str = None):
    # if not os.path.exists(file_path):
    # os.makedirs(file_path)

    # for idx, (video_url, caption) in enumerate(videos):
    video_url = url_desc[0]
    caption = url_desc[1]
    headers = (
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if headers is None
        else headers.get("headers")
    )
    for i in range(len(url_desc)):
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
            video_filename = os.path.join(file_path, f"{caption}.mp4")
            if os.path.exists(video_filename):
                print(f"Video {video_filename} already exists, skipping...")
                continue

            response = requests.get(video_url, headers=headers)
            with open(video_filename, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading video  {e}")


async def download_single_url(url_desc: tuple[str, str]):
    try:
        # 开始解析数据
        # try:
        #     data = await HybridCrawler().hybrid_parsing_single_video(
        #         url=url, minimal=True
        #     )
        # except Exception as e:
        #     print("hybrid_parsing_single_video 报错: ", e)
        #     return

        # description = data.get("desc").strip()
        # if len(description) > 1096:
        #     description = str(description.strip())[:1096]

        no_watermark_video_url = url_desc[0]
        description = url_desc[1]
        file_path = os.path.abspath(
            os.path.join("downloads_tiktok", description + ".mp4")
        )
        if os.path.exists(file_path):
            print(f"已存在, 跳过: {no_watermark_video_url}")
            return
        __headers = await HybridCrawler().TikTokWebCrawler.get_tiktok_headers()
        # no_watermark_video_url = data.get("video_data").get("nwm_video_url_HQ")
        success = download_video(
            no_watermark_video_url, headers=__headers, file_path=file_path
        )
        if not success:
            print(f"下载失败: {no_watermark_video_url}")
    except Exception as e:
        print("error: ", e)


async def parse_tiktok_urls(urls: List[str]):
    # 开始解析数据
    ret_data = []
    for url in urls:
        try:
            data = await HybridCrawler().hybrid_parsing_single_video(
                url=url, minimal=True
            )
            no_watermark_video_url = data.get("video_data").get("nwm_video_url_HQ")
            description = data.get("desc").strip()
            if len(description) > 200:
                description = str(description.strip())[:200]
            description = description.replace("/", "_")
            ret_data.append((no_watermark_video_url, description))
        except Exception as e:
            print("hybrid_parsing_single_video 报错: ", e)
            # return
    return ret_data


def download_url_wrapper(url_desc):
    # 在单独的进程中运行异步函数
    asyncio.run(download_single_url(url_desc))


def download_tiktok_urls(url_descs: list):
    # 创建下载目录
    os.makedirs("downloads_tiktok", exist_ok=True)

    # 使用多进程池
    with Pool(cpu_count() - 1) as pool:
        pool.map(download_url_wrapper, url_descs)


# 获取页面内容
async def get_page_videos(url):
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

            url_descs = await parse_tiktok_urls(r)
            download_tiktok_urls(url_descs)
            print("==================")
            print(r)
            print("==================")
            while time.time() - tmp_start < 20:
                await asyncio.sleep(1)
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
            if video_share_url not in url_sets:
                videos.append(video_share_url)
                url_sets.add(video_share_url)
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

    pages = [
        # "https://www.tiktok.com/tag/meme",
        # "https://www.tiktok.com/tag/funny",
        "https://www.tiktok.com/tag/food",
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
    for url in pages:
        try:
            await get_page_videos(url)
        except Exception as e:
            print(f"Error getting videos from {url}: {e}")
            traceback.print_exc()
    pass


if __name__ == "__main__":
    asyncio.run(main())
