import os
import hashlib
import base64
import csv
import random
from moviepy import VideoFileClip

# 定义视频目录路径
video_dir = "video"

# 定义输出的 CSV 文件路径
csv_file = "video_info.csv"


def gen_ticker(filename: str):

    words = (
        filename.strip().replace("'", "").replace('"', "").replace(" ", ",").split(",")
    )
    if len(words) == 0:
        return "MVMT"

    if len(words) == 1:
        if len(words[0]) > 3:
            return words[0][:4]
        else:
            return words[0] + "VT"
    elif len(words) == 2:
        return words[0][:2] + words[1][:2]
    elif len(words) == 3:
        return words[0][:1] + words[1][:1] + words[2][:1] + "T"
    elif len(words) > 4:
        return words[0][:1] + words[1][:1] + words[2][:1] + words[3][:1]


def main2():

    for filename in os.listdir(video_dir):
        file_path = os.path.join(video_dir, filename)
        new_file_path = file_path.replace('.mp4', '') + '.mp4'
        os.rename(file_path, new_file_path)
        # os.rename(file_path, file_path + ".mp4")
    pass


def main3():

    thumbnail = 'thumbnail'
    for filename in os.listdir(thumbnail):
        file_path = os.path.join(thumbnail, filename)
        new_file_path = file_path.replace('.mp4', '')
        os.rename(file_path, new_file_path)
    pass


def main():

    # 打开 CSV 文件进行写入
    with open(csv_file, mode="a+", newline="") as csvfile:

        fieldnames = ["name", "symbol", "description", "seconds"]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 写入 CSV 文件表头
        writer.writeheader()

        # 遍历视频目录中的所有文件
        for filename in os.listdir(video_dir):
            if ' ' not in filename: continue
            file_path = os.path.join(video_dir, filename)

            # 如果是视频文件
            if os.path.isfile(file_path):
                # 获取视频的描述（原文件名）
                description = filename.replace(".mp4", "")

                # 计算文件的哈希值
                with open(file_path, "rb") as f:
                    file_hash = hashlib.sha256(f.read()).digest()

                # 将哈希值转换为 Base64 编码
                base32_hash = (
                    base64.b32encode(file_hash).decode("utf-8").replace("=", "")[:20]
                )

                # 获取视频的时长（秒）
                video_clip = VideoFileClip(file_path)
                duration = video_clip.duration

                # 获取新文件名（哈希值的 Base64 编码）
                new_name = base32_hash + os.path.splitext(filename)[1]

                # 重命名视频文件
                new_file_path = os.path.join(video_dir, new_name.strip())
                os.rename(file_path, new_file_path)

                symbol = gen_ticker(filename.replace(".mp4", ""))
                if not symbol: symbol = 'MVVT'
                symbol = symbol.upper()

                # 写入 CSV 文件
                writer.writerow(
                    {
                        "name": new_name,
                        "symbol": symbol,
                        "description": description.replace('.mp4', ''),
                        "seconds": duration,
                    }
                )

                print(
                    f"Renamed: {filename} -> {new_name} | Duration: {duration} seconds"
                )


if __name__ == "__main__":
    main()

    # print(gen_ticker('You are'))
    # main2()
    # main3()
