import asyncio
import os
import sys
from threading import Thread
import traceback
from typing import List
import httpx
import requests
import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# 添加 Douyin_TikTok_Download_API
current_dir = os.path.dirname(os.path.abspath(__file__))
a_dir = os.path.abspath(os.path.join(current_dir, "Douyin_TikTok_Download_API"))
sys.path.append(a_dir)
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


def download_video(url, caption, headers: dict = None, file_path: str = None):
    # if not os.path.exists(file_path):
    # os.makedirs(file_path)

    # for idx, (video_url, caption) in enumerate(videos):
    # video_url = url_desc[0]
    # caption = url_desc[1]
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
        # if not success:
        # print(f"下载失败: {no_watermark_video_url}")
    except Exception as e:
        print("error: ", e)


async def parse_tiktok_urls(urls: List[str], tag: str):
    # 开始解析数据
    ret_data = []

    threads = []
    for url in urls:
        try:

            # TODO: 为什么解析url很慢??
            data = await HybridCrawler().hybrid_parsing_single_video(
                url=url, minimal=True
            )
            no_watermark_video_url = data.get("video_data").get("nwm_video_url_HQ")
            description = data.get("desc").strip()
            if len(description) > 200:
                description = str(description.strip())[:200]
            description = description.replace("/", "_")
            ret_data.append((no_watermark_video_url, description, tag))

            t = Thread(
                target=download_url_wrapper,
                args=((no_watermark_video_url, description, tag),),
            )
            t.start()
            threads.append(t)
        except Exception as e:
            print("hybrid_parsing_single_video 报错: ", e)
            # return
    for t in threads:
        t.join()
    return ret_data


def download_url_wrapper(url_desc_tag):
    # 在单独的进程中运行异步函数
    asyncio.run(
        download_single_url(
            url_desc_tag,
        )
    )


# 获取页面内容
async def get_page_videos(url, tag: str):
    driver.get(url)
    start_time = time.time()

    await asyncio.sleep(5)
    # 使用 set去重
    ret_videos = set()
    # 获取初始滚动高度
    last_height = driver.execute_script("return document.body.scrollHeight")
    while time.time() - start_time < 5 * 60 * 60:
        try:
            try:
                # 处理首次打开页面报错， 需要点击"刷新"
                error_div = driver.find_element(
                    By.CLASS_NAME, "css-1osbocj-DivErrorContainer"
                )
                if error_div:
                    fresh_button = error_div.find_element(By.TAG_NAME, "button")
                    fresh_button.click()
                    time.sleep(5)
            except NoSuchElementException as e:
                print("页面打开正常")
            except Exception as e:
                print("error: " + str(e))


            print("scrolling...")
            # 滚到到底部
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(3)

            # 休眠几秒，等待页面加载
            await asyncio.sleep(5)
            try_times = 0
            new_height = 0
            while try_times < 3:
                try:
                    new_height = driver.execute_script(
                        "return document.body.scrollHeight"
                    )
                    if new_height == last_height:
                        driver.execute_script(
                            "window.scrollTo(0, document.body.scrollHeight);"
                        )
                        await asyncio.sleep(10)
                    else:
                        break
                except Exception as e:
                    print(f"Error scrolling: {e}")
                finally:
                    try_times += 1
            if new_height == last_height:
                print("滚动到底部了，已经滚不动了")
                break

            last_height = new_height
        except Exception as e:
            print(f"Error scrolling: {e}")
            continue

        r = get_video_share_url()
        if len(r) > 0:
            ret_videos.update(r)
            tmp_start = time.time()

            await parse_tiktok_urls(r, tag)
            print("==================")
            print(r)
            print("==================")
            while time.time() - tmp_start < 10:
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(10)

        pass

    return []


def get_video_share_url():
    """
    获取页面中的视频和文案
    """
    videos = []

    video_div_list = []
    try:
        # 等待页面加载完成后查找视频
        for i in range(3):
            print("get_video_and_text_ex")
            video_div_list = driver.find_elements(
                By.CLASS_NAME, "css-x6y88p-DivItemContainerV2"
            )
            print("vidoe_list length:", len(video_div_list))

            if len(video_div_list) > 0:
                break

            # 刷新页面
            if len(video_div_list) == 0:
                driver.refresh()
                time.sleep(5)
                video_div_list = driver.find_elements(
                    By.CLASS_NAME, "css-x6y88p-DivItemContainerV2"
                )
    except Exception as e:
        driver.refresh()
        return videos

    for video_div in video_div_list:
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

    pages = [
        # "https://www.tiktok.com/tag/meme",
        # "https://www.tiktok.com/tag/funny",
        # "https://www.tiktok.com/tag/food",
        # "https://www.tiktok.com/tag/dancing",
        # "https://www.tiktok.com/tag/dance",
        # "https://www.tiktok.com/tag/eating",
        # "https://www.tiktok.com/tag/fyp",
        # "https://www.tiktok.com/tag/foryou",
        # "https://www.tiktok.com/tag/foryoupage",
        # "https://www.tiktok.com/tag/funnyvideos",
        # "https://www.tiktok.com/tag/fy",
        # "https://www.tiktok.com/tag/prank",
        # "https://www.tiktok.com/tag/fun",
        # "https://www.tiktok.com/tag/pets",
        # "https://www.tiktok.com/tag/anime",
        "https://www.tiktok.com/tag/beauty",
        # "https://www.tiktok.com/tag/basketball",
        "https://www.tiktok.com/tag/dancer",
        "https://www.tiktok.com/tag/relax",
        "https://www.tiktok.com/tag/relaxing",
        "https://www.tiktok.com/tag/scenery",
        "https://www.tiktok.com/tag/massage",
        "https://www.tiktok.com/tag/spa",
        "https://www.tiktok.com/tag/behappy",
        "https://www.tiktok.com/tag/hopecore",
        "https://www.tiktok.com/tag/positivity",
        "https://www.tiktok.com/tag/wholesome",
        "https://www.tiktok.com/tag/trading",
        "https://www.tiktok.com/tag/memecoin",
        "https://www.tiktok.com/tag/couple",
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
        "https://www.tiktok.com/tag/onthisday",
        "https://www.tiktok.com/tag/outfit",
        "https://tiktok.com/tag/parati",
        "https://tiktok.com/tag/paratii",
        "https://tiktok.com/tag/pourtoi",
        "https://tiktok.com/tag/paratiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",
        "https://tiktok.com/tag/pov",
        "https://tiktok.com/tag/satisfying",
        "https://tiktok.com/tag/storytime",
        "https://tiktok.com/tag/standwithkashmir",
        "https://tiktok.com/tag/trending",
        "https://tiktok.com/tag/trendingvideo",
        "https://tiktok.com/tag/tiktok",
        "https://tiktok.com/tag/tiktokviral",
        "https://tiktok.com/tag/usa",
        "https://www.tiktok.com/tag/viral",
        "https://www.tiktok.com/tag/viralvideo",
        "https://www.tiktok.com/tag/video",
        "https://www.tiktok.com/tag/macau",
        "https://www.tiktok.com/tag/you",
        "https://www.tiktok.com/tag/zoommyface",
        "https://www.tiktok.com/tag/amor",
        "https://www.tiktok.com/tag/bts",
        "https://www.tiktok.com/tag/Netherlands",
        "https://www.tiktok.com/tag/amsterdam",
        "https://www.tiktok.com/tag/redlights",
        "https://www.tiktok.com/tag/bitcoin",
        "https://www.tiktok.com/tag/solana",
        "https://www.tiktok.com/tag/crypto",
        "https://www.tiktok.com/tag/baby",
        "https://www.tiktok.com/tag/challenge",
        "https://www.tiktok.com/tag/dog",
        "https://www.tiktok.com/tag/dress",
        "https://www.tiktok.com/tag/dc",
        "https://www.tiktok.com/tag/indonesia",
        "https://www.tiktok.com/tag/thailand",
        "https://www.tiktok.com/tag/japan",
        "https://www.tiktok.com/tag/justforfun",
        "https://www.tiktok.com/tag/kpopfyp",
        "https://www.tiktok.com/tag/live",
        "https://www.tiktok.com/tag/sexy",
        "https://www.tiktok.com/tag/girls",
        "https://www.tiktok.com/tag/hotgirls",
        "https://www.tiktok.com/tag/hotgirl",
        "https://www.tiktok.com/tag/hotbody",
        "https://www.tiktok.com/tag/pretty",
        "https://www.tiktok.com/tag/prettygirls",
        "https://www.tiktok.com/tag/prettygirl",
        "https://www.tiktok.com/tag/%E6%BC%82%E4%BA%AE",
        "https://www.tiktok.com/tag/perfectgirl",
        "https://www.tiktok.com/tag/bikini",
        "https://www.tiktok.com/tag/dancinggirl",
        "https://www.tiktok.com/tag/fyppppppppppppppppppppppp",
        "https://www.tiktok.com/tag/asiangirl",
        "https://www.tiktok.com/tag/japangirl",
        "https://www.tiktok.com/tag/japanesegirl",
        "https://www.tiktok.com/tag/kawaiigirl",
        "https://www.tiktok.com/tag/%E5%8F%AF%E6%84%9B%E3%81%84",
        "https://www.tiktok.com/tag/lovely",
        "https://www.tiktok.com/tag/sweats",
        "https://www.tiktok.com/tag/sweaty",
        "https://www.tiktok.com/tag/fitness",
        "https://www.tiktok.com/tag/gymgirl",
        "https://www.tiktok.com/tag/gym",
        "https://www.tiktok.com/tag/gymboy",
        "https://www.tiktok.com/tag/man",
        "https://www.tiktok.com/tag/tiktokdance",
        "https://www.tiktok.com/tag/chinesegirl",
        "https://www.tiktok.com/tag/dancechallenge",
        "https://www.tiktok.com/tag/woman",
        "https://www.tiktok.com/tag/women",
        "https://www.tiktok.com/tag/girls",
        "https://www.tiktok.com/tag/beautiful",
        "https://www.tiktok.com/tag/beautygrils",
        "https://www.tiktok.com/tag/beautygril",
        "https://www.tiktok.com/tag/tiktoktravel",
        "https://www.tiktok.com/tag/roadtrip",
        "https://www.tiktok.com/tag/dancer",
        "https://www.tiktok.com/tag/koreangirl",
        "https://www.tiktok.com/tag/%EC%B6%94%EC%B2%9C",
        "https://www.tiktok.com/tag/blackgirl",
        "https://www.tiktok.com/tag/africa",
        "https://www.tiktok.com/tag/spain",
        "https://www.tiktok.com/tag/spanish",
        "https://www.tiktok.com/tag/italy",
        "https://www.tiktok.com/tag/footbool",
        "https://www.tiktok.com/tag/vietnam",
        "https://www.tiktok.com/tag/tiktokvietnam",
        "https://www.tiktok.com/tag/german",
        "https://www.tiktok.com/tag/germany",
        "https://www.tiktok.com/tag/deutschland",
        "https://www.tiktok.com/tag/deutsch",
        "https://www.tiktok.com/tag/france",
        "https://www.tiktok.com/tag/paris",
        "https://www.tiktok.com/tag/sunset",
        "https://www.tiktok.com/tag/aesthetic",
        "https://www.tiktok.com/tag/boyfriend",
        "https://www.tiktok.com/tag/girlfriend",
        "https://www.tiktok.com/tag/lovelife",
        "https://www.tiktok.com/tag/portugal%F0%9F%87%B5%F0%9F%87%B9",
        "https://www.tiktok.com/tag/portugal",
        "https://www.tiktok.com/tag/usa",
        "https://www.tiktok.com/tag/singapore",
        "https://www.tiktok.com/tag/malaysia",
        "https://www.tiktok.com/tag/mardan",
        "https://www.tiktok.com/tag/luxury",
        "https://www.tiktok.com/tag/richlife",
        "https://www.tiktok.com/tag/dubai",
        "https://www.tiktok.com/tag/luxurylife",
        "https://www.tiktok.com/tag/rich",
        "https://www.tiktok.com/tag/oldmoney",
        "https://www.tiktok.com/tag/lifestyle",
        "https://www.tiktok.com/tag/shopping",
        "https://www.tiktok.com/tag/fashion",
        "https://www.tiktok.com/tag/black",
        "https://www.tiktok.com/tag/car",
        "https://www.tiktok.com/tag/cars",
        "https://www.tiktok.com/tag/supercars",
        "https://www.tiktok.com/tag/ferrari",
        "https://www.tiktok.com/tag/motorcycle",
        "https://www.tiktok.com/tag/moto",
        "https://www.tiktok.com/tag/money",
        "https://www.tiktok.com/tag/australia",
        "https://www.tiktok.com/tag/sydney",
        "https://www.tiktok.com/tag/city",
        "https://www.tiktok.com/tag/airplane",
        "https://www.tiktok.com/tag/country",
        "https://www.tiktok.com/tag/switzerland",
        "https://www.tiktok.com/tag/village",
        "https://www.tiktok.com/tag/beach",
        "https://www.tiktok.com/tag/sunrise",
        "https://www.tiktok.com/tag/goodmorning",
        "https://www.tiktok.com/tag/russia",
        "https://www.tiktok.com/tag/russiagirl",
        "https://www.tiktok.com/tag/russiagirls",
        "https://www.tiktok.com/tag/russian",
        "https://www.tiktok.com/tag/russiangirl",
        "https://www.tiktok.com/tag/moscow",
        "https://www.tiktok.com/tag/nightlife",
        "https://www.tiktok.com/tag/tokyo",
        "https://www.tiktok.com/tag/newzealand",
        "https://www.tiktok.com/tag/southafrica",
        "https://www.tiktok.com/tag/hawaii",
        "https://www.tiktok.com/tag/tibet",
        "https://www.tiktok.com/tag/india",
        "https://www.tiktok.com/tag/tiktokindia",
        "https://www.tiktok.com/tag/china",
        "https://www.tiktok.com/tag/xuhong",
        "https://www.tiktok.com/tag/jakarta",
        "https://www.tiktok.com/tag/iran",
        "https://www.tiktok.com/tag/pakistan",
        "https://www.tiktok.com/tag/turkey",
        "https://www.tiktok.com/tag/brazil",
        "https://www.tiktok.com/tag/agentina",
        "https://www.tiktok.com/tag/colombia",
        "https://www.tiktok.com/tag/Uruguay",
        "https://www.tiktok.com/tag/england",
        "https://www.tiktok.com/tag/london",
        "https://www.tiktok.com/tag/livepool",
        "https://www.tiktok.com/tag/canada",
        "https://www.tiktok.com/tag/canadiangirl",
        "https://www.tiktok.com/tag/newyork",
        "https://www.tiktok.com/tag/nyc",
        "https://www.tiktok.com/tag/washington",
        "https://www.tiktok.com/tag/us",
        "https://www.tiktok.com/tag/traveltiktok",
        "https://www.tiktok.com/tag/chinatravel",
        "https://www.tiktok.com/tag/summer",
        "https://www.tiktok.com/tag/spring",
        "https://www.tiktok.com/tag/winter",
        "https://www.tiktok.com/tag/snow",
        "https://www.tiktok.com/tag/cargirl",
        "https://www.tiktok.com/tag/carmodel",
        "https://www.tiktok.com/tag/model",
        "https://www.tiktok.com/tag/actress",
        "https://www.tiktok.com/tag/idol",
        "https://www.tiktok.com/tag/hottrend",
        "https://www.tiktok.com/tag/pinay",
        "https://www.tiktok.com/tag/lux",
        "https://www.tiktok.com/tag/success",
        "https://www.tiktok.com/tag/billionaire",
        "https://www.tiktok.com/tag/food",
        "https://www.tiktok.com/tag/tiktokfood",
        "https://www.tiktok.com/tag/streetfood",
        "https://www.tiktok.com/tag/bread",
        "https://www.tiktok.com/tag/bbq",
        "https://www.tiktok.com/tag/relationship",
        "https://www.tiktok.com/tag/sweetcouple",
        "https://www.tiktok.com/tag/loveyou",
        "https://www.tiktok.com/tag/xyzbca",
        "https://www.tiktok.com/tag/capcut",
        "https://www.tiktok.com/tag/ai",
        "https://www.tiktok.com/tag/asian",
        "https://www.tiktok.com/tag/%E6%97%A5%E6%9C%AC",
        "https://www.tiktok.com/tag/%E6%B2%96%E7%B8%84",
        "https://www.tiktok.com/tag/sjk",
        "https://www.tiktok.com/tag/jk",
        "https://www.tiktok.com/tag/seoul",
        "https://www.tiktok.com/tag/korean",
        "https://www.tiktok.com/tag/%EC%B6%94%EC%B2%9C",
        "https://www.tiktok.com/tag/%EC%B6%94%EC%B2%9C%EB%96%A0%EB%9D%BC",
        "https://www.tiktok.com/tag/swim",
        "https://www.tiktok.com/tag/today",
        "https://www.tiktok.com/tag/%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B8%87%E0%B8%B2%E0%B8%A1",
        "https://www.tiktok.com/tag/%E0%B8%99%E0%B8%B2%E0%B8%87%E0%B9%81%E0%B8%9A%E0%B8%9A",
        "https://www.tiktok.com/tag/thaigirl",
        "https://www.tiktok.com/tag/thai",
        "https://www.tiktok.com/tag/earthquake",
        "https://www.tiktok.com/tag/scary",
        "https://www.tiktok.com/tag/tutorial",
        "https://www.tiktok.com/tag/finland",
        "https://www.tiktok.com/tag/Lapland",
        "https://www.tiktok.com/tag/aurora",
        "https://www.tiktok.com/tag/body",
        "https://www.tiktok.com/tag/drink",
        "https://www.tiktok.com/tag/party",
        "https://www.tiktok.com/tag/vibe",
        "https://www.tiktok.com/tag/club",
        "https://www.tiktok.com/tag/casino",
        "https://www.tiktok.com/tag/jackpot",
        "https://www.tiktok.com/tag/myanmartiktok"
        "https://www.tiktok.com/tag/Myanmargirl",
        "https://www.tiktok.com/tag/cutegirl",
        "https://www.tiktok.com/tag/makemoney",
        "https://www.tiktok.com/tag/donaldtrump",
        "https://www.tiktok.com/tag/selfimprovement",
        "https://www.tiktok.com/tag/elonmusk",
        "https://www.tiktok.com/tag/robot",
        "https://www.tiktok.com/tag/wallstreet",
        "https://www.tiktok.com/tag/manhattan",
        "https://www.tiktok.com/tag/Lhasa",
        "https://www.tiktok.com/tag/menstyle",
        "https://www.tiktok.com/tag/mensfashion",
        "https://www.tiktok.com/tag/menswear",
        "https://www.tiktok.com/tag/cooking",
        "https://www.tiktok.com/tag/skills",
        "https://www.tiktok.com/tag/sports",
        "https://www.tiktok.com/tag/volleyball",
        "https://www.tiktok.com/tag/tennis",
        "https://www.tiktok.com/tag/golf",
        "https://www.tiktok.com/tag/yoga",
        "https://www.tiktok.com/tag/work",
        "https://www.tiktok.com/tag/cat",
    ]
    for url in pages:
        try:
            tag = url.replace("https://www.tiktok.com/tag/", "").strip()
            if not os.path.exists(os.path.join("downloads_tiktok", tag)):
                os.makedirs(os.path.join("downloads_tiktok", tag), exist_ok=True)
            await get_page_videos(url, tag)
        except Exception as e:
            print(f"Error getting videos from {url}: {e}")
            traceback.print_exc()
    pass


if __name__ == "__main__":
    asyncio.run(main())
