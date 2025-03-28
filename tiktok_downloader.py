import asyncio
import json
import os
import random
import sys
import traceback
from types import CoroutineType

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
async def fetch_data_stream(url: str, headers: dict = None, file_path: str = None):
    headers = (
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if headers is None
        else headers.get("headers")
    )
    async with httpx.AsyncClient() as client:
        # 启用流式请求
        print(f"流式下载url: {url}")
        async with client.stream("GET", url, headers=headers) as response:
            response.raise_for_status()

            # 流式保存文件
            async with aiofiles.open(file_path, "wb") as out_file:
                async for chunk in response.aiter_bytes():
                    # if await request.is_disconnected():
                    #     print("客户端断开连接，清理未完成的文件")
                    #     await out_file.close()
                    #     os.remove(file_path)
                    #     return False
                    await out_file.write(chunk)
            return True


async def download_tiktok_urls(urls: str):
    # 开始解析数据/Start parsing data
    for url in urls:
        try:
            data = await HybridCrawler().hybrid_parsing_single_video(url=url, minimal=True)

            description = data.get("desc")
            file_path = os.path.abspath(os.path.join("downloads_tiktok", description + ".mp4"))
            __headers = await HybridCrawler().TikTokWebCrawler.get_tiktok_headers()
            no_watermark_video_url = data.get("video_data").get("nwm_video_url_HQ")
            success = await fetch_data_stream(
                no_watermark_video_url, headers=__headers, file_path=file_path
            )
            if not success:
                print(f"下载失败: {url}")
        except Exception as e:
            code = 400
            print("error: ", e)
            return
    return


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

            # TODO:
            await download_tiktok_urls(r)
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
            videos.append(video_share_url)
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

    pages = ["https://www.tiktok.com/tag/meme"]
    for url in pages:
        try:
            await get_page_videos(url)
        except Exception as e:
            print(f"Error getting videos from {url}: {e}")
            traceback.print_exc()
    pass


if __name__ == "__main__":
    asyncio.run(main())
