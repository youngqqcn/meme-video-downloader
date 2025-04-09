import os
import shutil
import ffmpeg
import multiprocessing

INPUT_DIR = "video"  # 输入目录
OUTPUT_DIR = "new_video"  # 输出目录


# 转换函数
def convert_hevc_to_h264(input_file, output_file):
    try:
        print(f"正在转换: {input_file} 到 {output_file}")
        # 使用 ffmpeg-python 将 HEVC 视频转换为 H.264 格式
        ffmpeg.input(input_file).output(
            output_file,
            vcodec="libx264",
            acodec="aac",
            strict="experimental",
            preset="fast",
            crf=28,  # 18~28  , default 23, 值越小画质越高
        ).run()
        print(f"转换成功: {output_file}")
    except ffmpeg.Error as e:
        print(f"转换失败: {input_file} 错误: {e.stderr.decode()}")


# 处理单个视频文件的函数
def process_video(file_path):
    # 检查文件是否是 MP4 格式
    if file_path.endswith(".mp4"):
        # 获取视频文件的编码信息
        try:
            # 使用 ffprobe 获取视频编码信息
            probe = ffmpeg.probe(
                file_path,
                v="error",
                select_streams="v:0",
                show_entries="stream=codec_name",
            )
            codec = probe["streams"][0]["codec_name"]

            # 如果视频编码为 HEVC，则进行转换
            if codec == "hevc":
                # 生成输出文件路径，转换为 H.264 格式
                output_file = os.path.join(OUTPUT_DIR, os.path.basename(file_path))
                convert_hevc_to_h264(file_path, output_file)
            else:
                print(f"{file_path} 不需要转换（编码格式: {codec}）")
                # shutil.copy(
                #     file_path, os.path.join(OUTPUT_DIR, os.path.basename(file_path))
                # )
        except ffmpeg.Error as e:
            print(f"无法读取文件 {file_path}: {e.stderr.decode()}")

    else:
        print(f"{file_path} 不是 MP4 格式，跳过。")


# 遍历视频目录并处理文件
def process_videos_in_directory(directory):
    # 获取所有视频文件
    video_files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    # 使用多进程并行处理视频文件
    with multiprocessing.Pool(processes=multiprocessing.cpu_count() - 1) as pool:
        pool.map(process_video, video_files)


if __name__ == "__main__":
    # 视频目录
    video_directory = INPUT_DIR  # 你可以修改为你的视频目录路径

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)  # 创建输出目录

    # 确保视频目录存在
    if os.path.exists(video_directory):
        process_videos_in_directory(video_directory)
    else:
        print(f"视频目录 {video_directory} 不存在。")
