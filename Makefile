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
# s3cmd --recursive --skip-existing ./dir  s3://memevideo-static-online/idolx/dir