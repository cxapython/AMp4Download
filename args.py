# -*- coding: utf-8 -*-

import argparse
import random
import re
from zhconv import convert

import requests
from bs4 import BeautifulSoup

from fileinfo import FileInfo

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}


def get_parser():
    parser = argparse.ArgumentParser(description="Jable TV Downloader")
    parser.add_argument("--url", type=str, default="",
                        help="Jable TV URL to download")
    parser.add_argument("--keyword", type=str, default="",
                        help="根据关键词选择，前5页内容")

    return parser


def fetch(url):
    req = requests.get(url, headers=headers)
    source = req.text
    soup = BeautifulSoup(source, 'html.parser')
    h6_tags = soup.find_all('h6', class_='title')
    return h6_tags


def av_recommand(keyword):
    av_list = []
    h6_tags_all = []
    keyword = convert(keyword, "zh-hant")

    for i in range(1, 5):
        try:
            url = f"https://jable.tv/search/{keyword}/?q={keyword}&sort_by=post_date&from_videos=0{i}"
            h6_tags = fetch(url)
            h6_tags_all.extend(h6_tags)
        except Exception:
            pass

    for index, each in enumerate(h6_tags_all):
        url = each.next.attrs.get("href")
        title = each.text
        av_list.append(FileInfo(index=index, title=title, url=url))
    return av_list
