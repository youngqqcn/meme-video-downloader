import os
import hashlib
import base64
import csv
import random
import string
from moviepy import VideoFileClip

# 定义视频目录路径
video_dir = "video"

# 定义输出的 CSV 文件路径
csv_file = "video_info.csv"


def generate_random_string(length=4):
    # 生成一个包含所有字母和数字的字符集
    characters = string.ascii_letters  # 包含大小写字母和数字
    # 随机从字符集中选择字符，组成一个指定长度的随机字符串
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string.upper()


def gen_ticker(filename: str):

    # words = (
    #     filename.strip()
    #     .replace("*", "")
    #     .replace("#", "")
    #     .replace("!", "")
    #     .replace("'", "")
    #     .replace('"', "")
    #     .replace(" ", ",")
    #     .split(",")
    # )

    # if len(words) == 0:
    return generate_random_string(5)

    # if len(words) == 1:
    #     if len(words[0]) > 3:
    #         return words[0][:4]
    #     else:
    #         return words[0] + "VT"
    # elif len(words) == 2:
    #     if len(words[0]) >= 2 and len(words[1]) > 2:
    #         return words[0][:2] + words[1][:2]
    #     else:
    #         return generate_random_string(4)
    # elif len(words) == 3:
    #     return words[0][:1] + words[1][:1] + words[2][:1] + "T"
    # elif len(words) > 4:
    #     return words[0][:1] + words[1][:1] + words[2][:1] + words[3][:1]


def main():

    # 打开 CSV 文件进行写入
    with open(csv_file, mode="w", newline="") as csvfile:

        fieldnames = ["name", "symbol", "description", "seconds"]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 写入 CSV 文件表头
        writer.writeheader()

        video_paths = set(os.listdir(video_dir))

        mp4_video_paths = []

        # 去重
        video_hash_set = set()

        for x in video_paths:
            if x.startswith("."):
                print("删除.开头文件", x)
                os.remove( os.path.join(video_dir, x))

            if x.endswith(".mp4"):
                mp4_video_paths.append(x)
            else:
                # 删除非 mp4 文件
                print("删除非mp4", x)
                os.remove( os.path.join(video_dir, x))

        print("mp4_video_paths length: ", len(mp4_video_paths))
        # return

        # 遍历视频目录中的所有文件
        for filename in mp4_video_paths:
            file_path = os.path.join(video_dir, filename)

            # 如果是视频文件
            try:
                if os.path.isfile(file_path) and filename.endswith(".mp4"):
                    # 获取视频的描述（原文件名）
                    description = filename.replace(".mp4", "").strip()

                    # 计算文件的哈希值
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).digest()

                    # 将哈希值转换为 Base64 编码
                    base32_hash = (
                        base64.b32encode(file_hash)
                        .decode("utf-8")
                        .replace("=", "")[:20]
                    )

                    # 获取视频的时长（秒）
                    duration = 5
                    try:
                        video_clip = VideoFileClip(file_path)
                        duration = video_clip.duration
                    except Exception as e:
                        print(f"Error getting duration of {filename}: {e}")

                    # 获取新文件名（哈希值的 Base64 编码）
                    new_name = base32_hash + ".mp4"

                    # 重命名视频文件
                    new_file_path = os.path.join(video_dir, new_name.strip())
                    os.rename(file_path, new_file_path)

                    symbol = generate_random_string(5).upper()

                    # 去重
                    if new_name in video_hash_set:
                        print(new_name, "重复")
                        continue
                    video_hash_set.add(new_name)

                    # 写入 CSV 文件
                    writer.writerow(
                        {
                            "name": new_name,
                            "symbol": symbol,
                            "description": description.replace(".mp4", ""),
                            "seconds": duration,
                        }
                    )

                    print(
                        f"Renamed: {filename} -> {new_name} | Duration: {duration} seconds"
                    )
                else:
                    print(f"Skipping non-video file: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    main()
