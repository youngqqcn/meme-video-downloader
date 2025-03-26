import json
import pickle
import random
import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv
from selenium.webdriver.remote.webelement import WebElement

load_dotenv()


def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")

    # 试验
    options.add_argument("--disable-infobars")
    # options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    # Pass the argument 1 to allow and 2 to block
    options.add_experimental_option(
        "prefs", {"profile.default_content_setting_values.notifications": 1}
    )

    # 保存用户数据，避免重复登录
    options.add_argument("user-data-dir=./profile")  # 指定用户数据目录
    options.add_argument(
        "profile-directory=yqq"
    )  # 如果有多个 profile，可以指定具体的 profile

    return options


options = get_default_chrome_options()
options.binary_location = "chrome-linux64/chrome"
service = webdriver.ChromeService(executable_path="chromedriver-linux64/chromedriver")
driver = webdriver.Chrome(service=service, options=options)


def slow_typing(element: WebElement, text: str):
    element.click()
    for character in text:
        # 模拟键盘输入
        sleep_secs = random.randint(50, 100) / 100.0
        time.sleep(sleep_secs)
        element.send_keys(character)


def login_reddit():
    """
    不能直接使用 send_keys 去登录， reddit做了校验

    目前需要手动登录， 浏览器已经开启了cookie
    """

    # 打开 Reddit 登录页面
    # driver.get("https://www.reddit.com/")
    driver.get("https://www.reddit.com/r/funnyvideos/")

    # 等待按钮启用
    print(" 如果登录成功，手动关闭即可，浏览器保存了cookie")
    time.sleep(1000)
    pass


# 获取页面内容
def get_page_videos(url):
    driver.get(url)
    start_time = time.time()

    time.sleep(15)
    # 使用 set去重
    ret_videos = set()
    # 获取初始滚动高度
    last_height = driver.execute_script("return document.body.scrollHeight")
    while time.time() - start_time < 5 * 60 * 60:
        r = get_video_and_text_ex()
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
            download_videos(r)
            while time.time() - tmp_start < 10:
                time.sleep(1)
        else:
            time.sleep(10)

        # 休眠几秒，等待页面加载
        try_times = 0
        new_height = 0
        while try_times < 10:
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(15)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    time.sleep(3)
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


def get_video_and_text_ex():
    """
    获取页面中的视频和文案
    """
    videos = []

    # 等待页面加载完成后查找视频
    print("get_video_and_text_ex")
    article_list = driver.find_elements(By.TAG_NAME, "article")
    print("article_list length:", len(article_list))

    for article in article_list:
        try:
            post = article.find_element(By.TAG_NAME, "shreddit-post")
            post_title = post.get_attribute("post-title")
            post_type = post.get_attribute("post-type")
            if post_type != "video":
                continue

            player2 = post.find_element(By.TAG_NAME, "shreddit-player-2")

            media_json = player2.get_attribute("packaged-media-json")
            if media_json:
                media_metadata = json.loads(media_json)
                if (
                    "playbackMp4s" in media_metadata
                    and "permutations" in media_metadata["playbackMp4s"]
                    and len(media_metadata["playbackMp4s"]["permutations"]) > 0
                ):
                    # 取最后一个视频url
                    video_url = media_metadata["playbackMp4s"]["permutations"][-1][
                        "source"
                    ]["url"]
                    videos.append((video_url, post_title))
        except NoSuchElementException as e:
            print("video标签不存在: " + str(e))
        except Exception as e:
            print(f"Error extracting video or caption: {e}")

    return videos


def download_videos(videos, save_dir="downloads_reddit"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for idx, (video_url, caption) in enumerate(videos):
        try:
            print(f"Downloading video {idx+1}: {caption}")
            video_filename = os.path.join(save_dir, f"{caption}.mp4")
            if os.path.exists(video_filename):
                # 处理 maybemaybemaybe 频道的视频
                if caption.strip().lower() == "maybe maybe maybe":
                    video_filename = os.path.join(
                        save_dir, f"{caption}-{random.randint(1000, 999999)}.mp4"
                    )
                else:
                    print(f"Video {idx+1} already exists, skipping...")
                    continue

            response = requests.get(video_url)
            with open(video_filename, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading video {idx+1}: {e}")


# 主函数
def main():

    # 登录 Reddit
    # login_reddit()

    pages = [
        # "https://www.reddit.com/r/popular/",
        # "https://www.reddit.com/?feed=home",
        # "https://www.reddit.com/r/funny/",
        # "https://www.reddit.com/r/nextfuckinglevel/",
        # "https://www.reddit.com/r/interestingasfuck",
        # "https://www.reddit.com/r/mildlyinteresting",
        # "https://www.reddit.com/r/maybemaybemaybe", # 高质量
        # "http://reddit.com/r/MadeMeSmile/",
        # "https://www.reddit.com/r/Damnthatsinteresting",
        # "https://www.reddit.com/r/GuysBeingDudes/",
        # "https://www.reddit.com/r/BeAmazed",
        # "https://www.reddit.com/r/Wellthatsucks/",
        # "https://www.reddit.com/r/Unexpected",
        # "https://www.reddit.com/r/SipsTea",
        # "https://www.reddit.com/r/toptalent",
        # "https://www.reddit.com/r/RoastMe",
        # "https://www.reddit.com/r/oddlysatisfying",
        # "https://www.reddit.com/r/MadeMeSmile",
        # "https://www.reddit.com/r/woahdude",
        # "https://www.reddit.com/r/aww",
        # "https://www.reddit.com/r/AbsoluteUnits",
        # "https://www.reddit.com/r/blackmagicfuckery/"
        # "https://www.reddit.com/r/singularity/",
        # "https://www.reddit.com/r/OldSchoolCool",
        # "https://www.reddit.com/r/funnyvideos/",
        # "https://www.reddit.com/r/MemeVideos/",
        # "https://www.reddit.com/r/woahthatsinteresting/",
        # "https://www.reddit.com/r/sports/",
        "https://www.reddit.com/r/TikTokCringe", # 视频多
        "https://www.reddit.com/r/PeterExplainsTheJoke",
        "https://www.reddit.com/r/meirl",
        "https://www.reddit.com/r/memes",
        "https://www.reddit.com/r/powerwashingporn",
        "https://www.reddit.com/r/Eyebleach",
        "https://www.reddit.com/r/Philippines",
        "https://www.reddit.com/r/india",
        "https://www.reddit.com/r/malaysia",
        "https://www.reddit.com/r/korea",
        "https://www.reddit.com/r/japanlife",
        "https://www.reddit.com/r/singapore",
        "https://www.reddit.com/r/australia",
        "https://www.reddit.com/r/europe",
        "https://www.reddit.com/r/unitedkingdom",
        "https://www.reddit.com/r/CasualUK",
        "https://www.reddit.com/r/london",
        "https://www.reddit.com/r/canada",
        "https://www.reddit.com/r/brasil",
        "https://www.reddit.com/r/technology",
        "https://www.reddit.com/r/Futurology",
        "https://www.reddit.com/r/Scams",
        "https://www.reddit.com/r/Tinder",
        "https://www.reddit.com/r/woodworking",
        "https://www.reddit.com/r/DIY",
        "https://www.reddit.com/r/gardening",
        "https://www.reddit.com/r/malelivingspace",
        "https://www.reddit.com/r/houseplants",
        "https://www.reddit.com/r/Baking",
        "https://www.reddit.com/r/Breadit",
        "https://www.reddit.com/r/grilling",
        "https://www.reddit.com/r/Cooking",
        "https://www.reddit.com/r/shittyfoodporn",
        "https://www.reddit.com/r/Coffee",
        "https://www.reddit.com/r/camping",
        "https://www.reddit.com/r/hiking",
        "https://www.reddit.com/r/backpacking",
        "https://www.reddit.com/r/NatureIsFuckingLit",
        "https://www.reddit.com/r/UFOs",
        "https://www.reddit.com/r/aliens",
        "https://www.reddit.com/r/Weird",
        "https://www.reddit.com/r/blursedimages",
        "https://www.reddit.com/r/Fitness",
        "https://www.reddit.com/r/bodyweightfitness",
        "https://www.reddit.com/r/running",
        "https://www.reddit.com/r/productivity",
        "https://www.reddit.com/r/selfimprovement",
        "https://www.reddit.com/r/anime",
        "https://www.reddit.com/r/cosplay",
        "https://www.reddit.com/r/UrbanHell",
        "https://www.reddit.com/r/centuryhomes",
        "https://www.reddit.com/r/beauty",

    ]
    for url in pages:
        try:
            get_page_videos(url)
        except Exception as e:
            print(f"Error getting videos from {url}: {e}")


# 执行脚本
if __name__ == "__main__":
    main()
    driver.quit()  # 关闭浏览器
