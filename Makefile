# s3cmd 默认配置文件  ~/.s3cfg
# 查看目录大小
# s3cmd du s3://memevideo-static-online/idolx/video
# 上传文件
# s3cmd put yqq.txt s3://memevideo-static-online/idolx/
# 下载文件
# s3cmd get s3://memevideo-static-online/idolx/ tmp.txt
# 删除文件
# s3cmd del  s3://memevideo-static-online/idolx/yqq.txt
# 上传目录(递归)
# s3cmd sync --no-check-md5 --recursive --progress --skip-existing ./  s3://memevideo-static-online/idolx


# s3cmd sync --no-check-md5 --recursive --progress --skip-existing ./cover  s3://memevideo-static-online/idolx/

# s3cmd sync --no-check-md5 --recursive --progress --skip-existing ./logo  s3://memevideo-static-online/idolx/

# 会自动创建同名目录
# s3cmd sync --no-check-md5 --recursive --progress --skip-existing ./video  s3://memevideo-static-online/idolx/
# s3cmd sync --recursive --progress --skip-existing ./video  s3://memevideo-static-online/idolx/

# 覆盖
# s3cmd sync --no-check-md5 --force --recursive --progress  ./video  s3://memevideo-static-online/idolx/

# 覆盖
# s3cmd sync --check-md5 --force --recursive --progress  ./video  s3://memevideo-static-online/idolx/