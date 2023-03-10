#!/usr/bin/env python
# coding: utf-8
import os
import platform
import ssl
import urllib.request

import cloudscraper
import m3u8
from Crypto.Cipher import AES

from args import *
from config import headers
from cover import get_cover
from crawler import prepare_crawl
from delete import  delete_mp4
from merge import merge_ts_file, merge_mp4_file
import time
from rich.console import Console
from rich import print
from rich.table import Table
import re
import sys
console = Console()
ssl._create_default_https_context = ssl._create_unverified_context
parser = get_parser()
args = parser.parse_args()
sysinfo = platform.platform()


def run(url_list=None, target_name=None):
    if url_list is None:
        url_list = []
    # print("\n".join([f'序号:{each.index}  标题:{each.title}' for each in url_list]))
    if args.url.endswith(".m3u8"):
        item = args.url
        arr =  item.split("###")
        title = arr[0]
        m3u8_url =arr[-1]
        m3u8file = target_name.replace(".tmp", ".m3u8")
        dir_name = os.path.basename(target_name).replace(".tmp", "")
        temp_path = os.path.dirname(m3u8file)
        if "aarch64" in sysinfo:
            folder_path = os.path.join("/sdcard/av", dir_name)
        else:
            folder_path = os.path.join(os.getcwd(), dir_name)
        m3u8urlList = m3u8_url.split('/')
        m3u8urlList.pop(-1)
        download_url = '/'.join(m3u8urlList)
        console.log(f"上次下载的是，现在继续下载:{title}")
    else:
        if args.url:
            url = args.url
            title = ""

        else:
            index = console.input('输入想要下载视频序号,从0开始,输入q退出:')
            if index == "q":
                sys.exit()
            # 建立文件夹
            if not index:
                item = random.choice(url_list)
            else:
                item = url_list[int(index)]
            url = item.url
            title = item.title

        urlSplit = url.split('/')
        dir_name = urlSplit[-2]
        if dir_name == "vodplay":
            dir_name = str(int(time.time()))
        if "aarch64" in sysinfo:
            folder_path = os.path.join("/sdcard/av", dir_name)
        else:
            folder_path = os.path.join(os.getcwd(), dir_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # 得到 m3u8 网址
        resp = None
        for i in range(5):
            resp = cloudscraper.create_scraper(delay=10).get(url,headers=headers)
            if resp.status_code==200:
                break
        if not resp:
            sys.exit()
        result = re.search("http?s.+m3u8", resp.text)
        # 下载图片
        title=re.findall("<meta property=\"og:title\" content=\"(.*?)\"",resp.text)[0]
        console.log(f"当前下载的是:{title or dir_name}")
        get_cover(html_file=resp, folder_path=folder_path)
        m3u8url = result[0].replace("\\", "")
        m3u8urlList = m3u8url.split('/')
        m3u8urlList.pop(-1)
        download_url = '/'.join(m3u8urlList)

        #  m3u8 file 到文件
        temp_path = os.path.join(folder_path, f"{dir_name}_temp")
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        m3u8file = os.path.join(temp_path, dir_name + '.m3u8')
        tmp_file = os.path.join(temp_path, f"{dir_name}.tmp")
        with open(tmp_file, "w") as fs:
            fs.write(f"{title}###{m3u8url}")
        for i in range(5):
            try:
                urllib.request.urlretrieve(m3u8url, m3u8file)
                break
            except Exception:
               pass

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
    # delete_m3u8(temp_path)

    # In[8]:

    # 下载ts片段到文件夹
    prepare_crawl(ci, temp_path, ts_list[:])

    # In[9]:
    # 生成ts文件列表，ffmpeg使用的
    ts_text_path = merge_ts_file(temp_path, ts_list[:])

    # 合成mp4
    merge_mp4_file(temp_path, folder_path, ts_text_path)

    # In[10]:

    # 删除子mp4
    delete_mp4(temp_path)


def show_data(url_list):
    table = Table(show_header=True, title=f"前{args.count}条数据展示", caption="输入序号回车")
    table.add_column("序号", justify="left")
    table.add_column("标题")
    for each in url_list:
        bango = re.split(r'[^a-zA-Z0-9-]+', each.title)[0]
        new_title = "[gold1]{}[/gold1]:{}".format(bango, each.title.replace(bango, "").strip())
        table.add_row(str(each.index),
                      f"[blue][link=https://jable.tv/videos/{bango}/]{new_title}[/link][/blue]")
    table.highlight = True
    console.print(table)


def check_temp_file():
    if "aarch64" in sysinfo:
        folder_path = "/sdcard/av"
    else:
        folder_path = os.path.dirname(__file__)
    continue_map = {}
    for each_item in os.listdir(folder_path):
        # root 表示当前正在访问的文件夹路径
        # dirs 表示该文件夹下的子目录名list
        # files 表示该文件夹下的文件list
        # 遍历文件
        if os.path.isdir(each_item) and "-" in each_item:
            temp_path = os.path.join(os.path.join(folder_path, each_item), f"{each_item}_temp")
            temp_file = os.path.join(temp_path, f"{each_item}.tmp")
            if os.path.exists(temp_file):
                with open(temp_file, "r") as fs:
                    m3u8_link = fs.read()
                    continue_map[temp_file] = m3u8_link
    return continue_map


if __name__ == '__main__':
    continue_item = check_temp_file()
    name_list = []
    url_list = []
    if continue_item:
        for name, url in continue_item.items():
            name_list.append(name)

    target_name = ""
    c_result="n"
    if name_list:
        c_result = console.input("检测到上次有未继续下载的视频是否继续，Y or N:\n").lower()
    if c_result=="y" or not c_result.strip():
        if len(name_list) == 1:
            target_name = name_list[0]
            url = continue_item[target_name]
        else:
            print("name_list",name_list)
            c_index = console.input('输入想要继续下载的序号,从0开始:')
            target_name = name_list[int(c_index)]
            url = continue_item[target_name]
        args.url = url
    elif args.url:
        # 使用者输入Jable网址
        # url = "https://jable.tv/videos/fsdss-077/"
        url = args.url
    else:
        url_list = av_recommand(args)
        show_data(url_list)
    while True:
        run(url_list=url_list, target_name=target_name)
        if len(url_list)>0:
            result = console.input("是否需要继续下载,退出请输入q")
            if result == "q":
                break
            show_data(url_list)
