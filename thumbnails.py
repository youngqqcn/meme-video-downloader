import os
import ffmpeg
from PIL import Image
# 定义视频目录和输出图片目录
video_dir = "video"
output_dir = "thumbnail"

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


def main():

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    videos = set(os.listdir(video_dir))
    print("videos length: ", len(videos))

    # 遍历视频目录中的所有文件
    for filename in videos:
        file_path = os.path.join(video_dir, filename)

        # 确保是文件且是视频格式（可扩展支持更多格式）
        if os.path.isfile(file_path) and filename.lower().endswith((".mp4")):
            # 生成图片文件路径
            image_filename = os.path.splitext(filename)[0].replace(".mp4", "") + ".png"
            image_path = os.path.join(output_dir, image_filename)

            if os.path.exists(image_path):
                continue

            # 保存视频的第一帧为图片
            save_first_frame(file_path, image_path)

            # 保存裁剪后的图像为 1:1 PNG
            # cv2.imwrite(image_path, cropped_frame)
            resize_to_square(image_path, image_path)
            print(f"Saved cropped first frame of {filename} as {image_filename}")
        else:
            print(f"Skipping non-video file: {filename}")

    pass


if __name__ == "__main__":
    main()
