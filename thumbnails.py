import os
import cv2

# 定义视频目录和输出图片目录
video_dir = "video"
output_dir = "thumbnail"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历视频目录中的所有文件
for filename in os.listdir(video_dir):
    file_path = os.path.join(video_dir, filename)

    # 确保是文件且是视频格式（可扩展支持更多格式）
    if os.path.isfile(file_path) and filename.lower().endswith(
        (".mp4", ".avi", ".mov", ".mkv", ".flv")
    ):
        # 读取视频
        cap = cv2.VideoCapture(file_path)

        # 读取第一帧
        success, frame = cap.read()

        if success:
            # 获取原始帧的高度和宽度
            height, width, _ = frame.shape

            # 计算裁剪区域的边长（取宽度和高度的最小值）
            crop_size = min(width, height)

            # 计算裁剪的起始坐标（以图像中心为基准）
            x_start = (width - crop_size) // 2
            y_start = (height - crop_size) // 2

            # 裁剪图像
            cropped_frame = frame[
                y_start : y_start + crop_size, x_start : x_start + crop_size
            ]

            # 生成图片文件路径
            image_filename = os.path.splitext(filename)[0].replace('.mp4', '') + ".png"
            image_path = os.path.join(output_dir, image_filename)

            # 保存裁剪后的图像为 PNG
            cv2.imwrite(image_path, cropped_frame)
            print(f"Saved cropped first frame of {filename} as {image_filename}")

        # 释放资源
        cap.release()
