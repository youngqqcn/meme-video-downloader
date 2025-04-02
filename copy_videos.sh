#!/bin/bash


# 定义目录路径
DOWNLOADS_DIR="./downloads_tiktok"
VIDEO_DIR="./video"

# 确保 video 目录存在
mkdir -p "$VIDEO_DIR"

# 递归拷贝 downloads 目录下所有子目录中的 .mp4 文件到 video 目录
find "$DOWNLOADS_DIR" -type f -name "*.mp4" -exec cp {} "$VIDEO_DIR" \;

echo "completed"