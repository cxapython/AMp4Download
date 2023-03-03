# -*- coding: utf-8 -*-
# @时间 : 2023/3/3 11:38 下午
# @作者 : 陈祥安
# @文件名 : fileinfo.py
# @公众号: Python学习开发
from dataclasses import dataclass
@dataclass
class FileInfo:
    index: int
    title: str
    url: str