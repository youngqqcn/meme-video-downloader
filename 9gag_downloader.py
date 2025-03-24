import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
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
    while time.time() - start_time <  6:
        # r = get_video_and_text()
        r = get_video_and_text_ex()
        if len(r):
            ret_videos.update(r)
        time.sleep(3)
        print("scrolling...")
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as e:
            print(f"Error scrolling: {e}")
    return ret_videos


# 下载视频
def download_video(video_url, filename):
    response = requests.get(video_url)
    with open(filename, "wb") as f:
        f.write(response.content)


# # 获取页面上的所有视频链接及文案
def get_video_and_text():
    videos = []
    # 等待页面加载完成后查找视频

    # article_list = driver.find_elements(By.CLASS_NAME, "list-container")

    posts = driver.find_elements(By.CLASS_NAME, "post-view")
    print("posts length:", len(posts))


    for post in posts:
        try:
            video_tag = post.find_element(By.TAG_NAME, "video")
            # print('video tag: ', video_tag.text)
            if video_tag:
                # 查找所有的视频源
                sources = video_tag.find_elements(By.TAG_NAME, "source")
                video_url = None
                for source in sources:
                    video_type = source.get_attribute("type")
                    if "mp4" in video_type:
                        video_url = source.get_attribute("src")
                        break

                # 获取文案
                # caption_tag = post.find_element(By.CLASS_NAME, "length")
                # caption = caption_tag.text if caption_tag else "No caption"

                # if video_url:
                # videos.append((video_url, caption))
                if video_url:
                    videos.append(video_url)
        except Exception as e:
            print(f"Error extracting video or caption: {e}")

    return videos

def get_video_and_text_ex():
    videos = []
    # 等待页面加载完成后查找视频

    print('get_video_and_text_ex')
    # article_list = driver.find_elements(By.CLASS_NAME, "list-container")
    article_list = driver.find_elements(By.TAG_NAME, "article")

    print('article_list length:', len(article_list))

    for article in article_list:

        id = article.get_attribute("id")
        print('article id = ', id)




        # for post in posts:
        if True:
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
                    title = article.find_element(By.TAG_NAME, "header").find_element(By.TAG_NAME, "h2").text
                    print('article title = ', title)
                    videos.append((video_url, title))
            except NoSuchElementException as e:
                print("video标签不存在，跳过")
            except Exception as e:
                print(f"Error extracting video or caption: {e}")

    return videos


# 主函数
def main():
    videos = get_page_videos("https://9gag.com/top/")
    # videos = get_video_and_text()
    print("================================================")
    print(videos)

    # for idx, (video_url, caption) in enumerate(videos):
    #     try:
    #         print(f"Downloading video {idx+1}: {caption}")
    #         video_filename = os.path.join(save_dir, f"video_{idx+1}.mp4")
    #         download_video(video_url, video_filename)
    #         # 保存文案到文件
    #         with open(
    #             os.path.join(save_dir, f"caption_{idx+1}.txt"), "w", encoding="utf-8"
    #         ) as f:
    #             f.write(caption)
    #         print(f"Downloaded: {caption}")
    #     except Exception as e:
    #         print(f"Error downloading video {idx+1}: {e}")


# 执行脚本
if __name__ == "__main__":
    main()
    driver.quit()  # 关闭浏览器
