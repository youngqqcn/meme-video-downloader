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
    return options


options = get_default_chrome_options()
options.binary_location = "chrome-linux64/chrome"
service = webdriver.ChromeService(executable_path="chromedriver-linux64/chromedriver")
driver = webdriver.Chrome(service=service, options=options)


# 获取页面内容
def get_page_videos(url):
    driver.get(url)
    # last_height = driver.execute_script("return document.body.scrollHeight")

    start_time = time.time()

    # 使用 set去重
    ret_videos = set()
    while time.time() - start_time <10 * 60:
        # r = get_video_and_text()
        # time.sleep(2)
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
            download_videos(r)
        else:
            time.sleep(1)

        # if '/top' in url or '/trending' in url:
        if True:
            try:
                a = driver.find_element(By.CLASS_NAME, "btn end")
                if a is not None:
                    if a.text == "No more posts":
                        print("到底了")
                        break
            except NoSuchElementException as e:
                continue
            except Exception as e:
                print(f"error: {e}")

    return ret_videos


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
            video_tag = article.find_element(By.TAG_NAME, "video")
            if video_tag:
                # 查找所有的视频源
                sources = video_tag.find_elements(By.TAG_NAME, "source")
                video_url = None
                for source in sources:
                    video_type = source.get_attribute("type")
                    if "mp4" in video_type:
                        video_url = source.get_attribute("src")
                        break

                # 获取标题
                title = (
                    article.find_element(By.TAG_NAME, "header")
                    .find_element(By.TAG_NAME, "h2")
                    .text
                )
                title = title.strip()
                if title is None or len(title) == 0:
                    continue
                if len(title) >= 2048:
                    title = title[:2048]
                    continue

                print("article title = ", title)
                if os.path.exists(os.path.join("downloads", title + ".mp4")):
                    print(f"Video {title} already exists, skipping...")
                    continue
                videos.append((video_url, title))
        except NoSuchElementException as e:
            print("video标签不存在，跳过")
        except Exception as e:
            print(f"Error extracting video or caption: {e}")

    return videos


def download_videos(videos, save_dir="downloads"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for idx, (video_url, caption) in enumerate(videos):
        try:
            print(f"Downloading video {idx+1}: {caption}")
            video_filename = os.path.join(save_dir, f"{caption}.mp4")
            if os.path.exists(video_filename):
                print(f"Video {idx+1} already exists, skipping...")
                continue

            response = requests.get(video_url)
            with open(video_filename, "wb") as f:
                f.write(response.content)
        except Exception as e:
            print(f"Error downloading video {idx+1}: {e}")


# 主函数
def main():
    pages = [
        # 有底部
        # "https://9gag.com/home",
        # "https://9gag.com/top/",
        # "https://9gag.com/trending",
        # "https://9gag.com/tag/trump",
        "https://9gag.com/fresh"
        # 无底部
        # "https://9gag.com/interest/humor",
        # "https://9gag.com/interest/woah",
        # "https://9gag.com/interest/memes",
        # "https://9gag.com/interest/wtf",
        # "https://9gag.com/interest/animals",
        # "https://9gag.com/interest/games",
        # "https://9gag.com/interest/news",
        # "https://9gag.com/interest/relationship",
        # "https://9gag.com/interest/motorvehicles",
        # "https://9gag.com/interest/science",
        # "https://9gag.com/interest/comic",
        # "https://9gag.com/interest/wholesome",
        # "https://9gag.com/interest/sports",
        # "https://9gag.com/interest/movies",
        # "https://9gag.com/interest/cats",
        # "https://9gag.com/interest/food",
        # "https://9gag.com/interest/anime",
        # "https://9gag.com/interest/superhero",
        # "https://9gag.com/interest/lifestyle",
        # "https://9gag.com/interest/random",
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
