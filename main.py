import yt_dlp

URLS = ["https://www.youtube.com/shorts/FG-6cap1okc"]

# def longer_than_a_minute(info, *, incomplete):
#     """Download only videos longer than a minute (or with unknown duration)"""
#     duration = info.get('duration')
#     if duration and duration < 60:
#         return 'The video is too short'

# ydl_opts = {
#     'match_filter': longer_than_a_minute,
# }

with yt_dlp.YoutubeDL() as ydl:
    error_code = ydl.download(URLS)
