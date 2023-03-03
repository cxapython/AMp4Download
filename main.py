#!/usr/bin/env python
# coding: utf-8
import os
import platform
import ssl
import urllib.request

import cloudscraper
import m3u8
import requests
from Crypto.Cipher import AES

from args import *
from config import headers
from cover import get_cover
from crawler import prepare_crawl
from delete import delete_m3u8, delete_mp4
from merge import merge_ts_file, merge_mp4_file

ssl._create_default_https_context = ssl._create_unverified_context
parser = get_parser()
args = parser.parse_args()

if (len(args.url) != 0):
    url = args.url
elif (args.random == True):
    url = av_recommand()
else:
    # 使用者输入Jable网址
    #url = "https://jable.tv/videos/fsdss-077/"
    url = input('输入jable网址:')

# 建立文件夹
urlSplit = url.split('/')
dir_name = urlSplit[-2]
sysinfo = platform.platform()
if "aarch64" in sysinfo:
    folder_path = os.path.join("/sdcard", dir_name)
else:
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    folder_path = os.path.join(os.getcwd(), dir_name)

# 得到 m3u8 网址
htmlfile = cloudscraper.create_scraper(delay=10).get(url)
result = re.search("https://.+m3u8", htmlfile.text)
# 下载图片
get_cover(html_file=htmlfile, folder_path=folder_path)
m3u8url = result[0]
m3u8urlList = m3u8url.split('/')
m3u8urlList.pop(-1)
download_url = '/'.join(m3u8urlList)

#  m3u8 file 到文件
m3u8file = os.path.join(folder_path, dir_name + '.m3u8')
urllib.request.urlretrieve(m3u8url, m3u8file)

# In[5]:


# 得到 m3u8 file里的 URI和 IV
m3u8obj = m3u8.load(m3u8file)
m3u8_uri = ''
m3u8iv = ''

for key in m3u8obj.keys:
    if key:
        m3u8_uri = key.uri
        m3u8iv = key.iv

# 存储 ts网址 in ts_list
ts_list = []
for seg in m3u8obj.segments:
    tsUrl = download_url + '/' + seg.uri
    ts_list.append(tsUrl)

# In[6]:


# 有加密
if m3u8_uri:
    m3u8_key_url = download_url + '/' + m3u8_uri  # 得到 key 的地址
    # 得到 key的内容
    response = requests.get(m3u8_key_url, headers=headers, timeout=10)
    contentKey = response.content

    vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

    ci = AES.new(contentKey, AES.MODE_CBC, vt)
else:
    ci = ''

# In[7]:


# 删除m3u8 file
delete_m3u8(folder_path)

# In[8]:


# 下载ts片段到文件夹
prepare_crawl(ci, folder_path, ts_list[:])

# In[9]:
# 生成ts文件列表，ffmpeg使用的
ts_text_path = merge_ts_file(folder_path, ts_list[:])

# 合成mp4
merge_mp4_file(folder_path, ts_text_path)

# In[10]:


# 删除子mp4
delete_mp4(folder_path)
