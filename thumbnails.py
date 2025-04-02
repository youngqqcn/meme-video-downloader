import multiprocessing
import os
import threading
from typing import List
from PIL import Image
import ffmpeg

# 定义视频目录和输出图片目录
VIDEO_DIR = "video"
LOGO_DIR = "logo"
COVER_DIR = "cover"


def resize_to_square(image_path, output_path):
    # 打开图片
    img = Image.open(image_path)

    # 获取图片的宽高
    width, height = img.size

    # 计算裁剪区域的大小
    new_size = min(width, height)

    # 计算裁剪区域的位置，保持中心对齐
    left = (width - new_size) // 2
    top = (height - new_size) // 2
    right = (width + new_size) // 2
    bottom = (height + new_size) // 2

    # 裁剪图像
    img_cropped = img.crop((left, top, right, bottom))

    # 保存裁剪后的图片
    img_cropped.save(output_path)
    img_cropped.close()


def save_first_frame(video_path, output_image="first_frame.jpg"):
    ffmpeg.input(video_path).output(output_image, vframes=1).run()


def make_images(filename: str):

    file_path = os.path.join(VIDEO_DIR, filename)

    # 确保是文件且是视频格式（可扩展支持更多格式）
    if os.path.isfile(file_path) and filename.lower().endswith((".mp4")):
        # 生成图片文件路径
        image_filename = os.path.splitext(filename)[0].replace(".mp4", "") + ".png"
        logo_image_path = os.path.join(LOGO_DIR, image_filename)
        cover_image_path = os.path.join(COVER_DIR, image_filename)

        if not os.path.exists(cover_image_path):
            # 保存视频的第一帧为图片, 做封面图
            save_first_frame(file_path, cover_image_path)
        if not os.path.exists(logo_image_path):
            # 保存裁剪后的图像为 1:1 PNG
            resize_to_square(cover_image_path, logo_image_path)
        print(f"Saved cropped first frame of {filename} as {image_filename}")
    else:
        print(f"Skipping non-video file: {filename}")
    pass


def main():

    # 确保输出目录存在
    os.makedirs(LOGO_DIR, exist_ok=True)
    os.makedirs(COVER_DIR, exist_ok=True)

    videos = list(set(os.listdir(VIDEO_DIR)))
    print("videos length: ", len(videos))
    # print(videos[0])

    # 遍历视频目录中的所有文件

    mp_pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    mp_pool.map(make_images, videos)
    print("全部进程结束")
    mp_pool.close()
    mp_pool.join()

    pass


if __name__ == "__main__":
    main()
