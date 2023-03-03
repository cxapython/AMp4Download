import concurrent.futures
import os
import time
from functools import partial

import requests

from config import headers


def scrape(ci, folder_path, download_list, urls):
    os.path.split(urls)
    file_name = urls.split('/')[-1][0:-3]
    save_name = os.path.join(folder_path, file_name + ".ts")
    if os.path.exists(save_name):
        # 跳过已经下载
        print('当前目标: {0} 已下载, 故跳过...剩余 {1} 个'.format(
            urls.split('/')[-1], len(download_list)))
        download_list.remove(urls)
    else:
        response = requests.get(urls, headers=headers, timeout=10)
        if response.status_code == 200:
            content_ts = response.content
            if ci:
                content_ts = ci.decrypt(content_ts)  # 解碼
            with open(save_name, 'ab') as f:
                f.write(content_ts)
                # 输出进度
            download_list.remove(urls)
        print('\r当前下载: {0} , 剩余 {1} 个, status code: {2}'.format(
            urls.split('/')[-1], len(download_list), response.status_code), end='', flush=True)


def prepare_crawl(ci, folder_path, ts_list):
    download_list = ts_list
    # 開始時間
    start_time = time.time()
    print('开始下载 ' + str(len(download_list)) + ' 个文件..', end='')
    print('预计等待时间: {0:.2f} 分钟)'.format(len(download_list) / 150))

    # 開始爬取
    start_crawl(ci, folder_path, download_list)

    end_time = time.time()
    print('\n花费 {0:.2f} 分钟 爬取完成 !'.format((end_time - start_time) / 60))


def start_crawl(ci, folder_path, download_list):
    # 同時建立及啟用 20 個執行緒
    round = 0
    while (download_list != []):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(partial(scrape, ci, folder_path,
                                 download_list), download_list)
        round += 1
        print(f', round {round}')
