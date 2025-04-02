import os
import unicodedata

# def remove_non_unicode(text):
# return ''.join([c for c in text if unicodedata.category(c) != 'Cc'])


def remove_non_unicode(text):
    new_char = ""
    for char in text:
        if char not in [
            "\u2000",
            "\u2001",
            "\u2002",
            "\u2003",
            "\u2004",
            "\u2005",
            "\u2006",
            "\u2007",
            "\u2008",
            "\u2009",
            "\u200a",
            "\u200b",
            "\u200c",
            "\u200d",
            "\u200e",
            "\u200f",
            "\u2010",
            "\u2011",
            "\u2012",
            "\u2013",
            "\u2014",
            "\u2015",
            "\u2016",
            "\u2017",
            "\u2018",
            "\u2019",
            "\u201a",
            "\u201b",
            "\u201c",
            "\u201d",
            "\u201e",
            "\u201f",
            "\u2020",
            "\u2021",
            "\u2022",
            "\u2023",
            "\u2024",
            "\u2025",
            "\u2026",
            "\u2027",
            "\u2028",
            "\u2029",
            "\u202a",
            "\u202b",
            "\u202c",
            "\u202d",
            "\u202e",
            "\u202f",
            "\u2030",
        ]:
            new_char += char
    return new_char.encode("utf-8", errors="ignore").decode("utf-8")


with open("video_info.csv", "r") as infile, open("video_info_new.csv", "w") as outfile:
    lines = infile.readlines()
    outfile.write(lines[0])
    lines = lines[1:]
    for line in lines:
        if len(line.strip()) == 0:
            continue
        video = line.split(",")[0]
        print(video)
        if os.path.exists(os.path.join("video", video)):
            line = remove_non_unicode(line)
            outfile.write(line)


# def clean_non_utf8(file_path):
#     try:
#         # 读取文件内容，忽略无法解码的字节
#         with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
#             content = file.read()

#         # 将清理后的内容写回文件
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(content)

#         print(f"文件 '{file_path}' 已清理完成。")
#     except Exception as e:
#         print(f"处理文件时出错: {e}")

# clean_non_utf8('video_info_new.csv')
