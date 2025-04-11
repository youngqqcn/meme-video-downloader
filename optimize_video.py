import os
import subprocess
from pathlib import Path
import multiprocessing

# 定义原视频目录和目标视频目录
video_dir = Path('video')  # 原视频所在目录
new_video_dir = Path('new_video')  # 转换后的视频保存目录

# 确保目标目录存在
new_video_dir.mkdir(parents=True, exist_ok=True)

# 获取所有MP4文件
mp4_files = [f for f in video_dir.glob('*.mp4')]

# 定义转换函数
def process_video(input_file: Path):
    output_file = new_video_dir / input_file.name  # 输出路径
    cmd = [
        'ffmpeg',
        '-i', str(input_file),  # 输入文件
        '-c', 'copy',           # 使用拷贝模式（不重新编码）
        '-map', '0',            # 保留所有流
        '-movflags', '+faststart',  # 优化视频流式播放
        str(output_file)        # 输出文件
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"转换成功: {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"处理 {input_file} 时发生错误: {e}")

# 使用多进程处理多个文件
if __name__ == '__main__':
    # 设置进程池的大小，这里使用CPU的核心数
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(process_video, mp4_files)
