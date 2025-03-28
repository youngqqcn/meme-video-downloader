import asyncio
import os
import random
import sys

import aiofiles
import httpx
import requests

# 添加 Douyin_TikTok_Download_API
current_dir = os.path.dirname(os.path.abspath(__file__))
a_dir = os.path.abspath(os.path.join(current_dir, "Douyin_TikTok_Download_API"))
sys.path.append(a_dir)

# from crawlers.hybrid.hybrid_crawler import HybridCrawler
from Douyin_TikTok_Download_API.crawlers.hybrid.hybrid_crawler import HybridCrawler


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


async def download_tiktok(url: str):
    # 开始解析数据/Start parsing data
    try:
        data = await HybridCrawler().hybrid_parsing_single_video(url=url, minimal=True)
    except Exception as e:
        code = 400
        print("error: ", e)
        return
    description = data.get("desc")

    file_path = os.path.abspath(os.path.join("downloads_tiktok", description + ".mp4"))
    __headers = await HybridCrawler().TikTokWebCrawler.get_tiktok_headers()
    no_watermark_video_url = data.get("video_data").get("nwm_video_url_HQ")
    success = await fetch_data_stream(
        no_watermark_video_url, headers=__headers, file_path=file_path
    )
    if not success:
        print("下载失败")
        return


async def main():
    # share_url = "https://www.tiktok.com/@g1885068req/video/7483013990390582583?is_from_webapp=1&sender_device=pc"
    share_url = "https://www.tiktok.com/@notnayelig/video/7477658217661877550?is_from_webapp=1&sender_device=pc"
    await download_tiktok(share_url)
    pass


if __name__ == "__main__":
    asyncio.run(main())
