import os
import subprocess
import time

from loguru import logger


# merge_ts_file(folder_path, ts_list[:])
def merge_ts_file(folder_path, ts_list):
    for ts_url in ts_list:
        _ts_file = os.path.basename(ts_url)
        merge_text_path = os.path.join(folder_path, f"{int(time.time())}_merge_file.txt")
        with open(merge_text_path, "w+") as f:
            for index, file in enumerate(ts_list):
                content = f"file '{file}'\n"
                if index == len(ts_list) - 1:
                    content = f"file '{file}'"
                f.write(content)
        return merge_text_path


# folder_path, ts_text_path
def merge_mp4_file(folder_path, ts_text_path):
    mp4_file_name =f"{os.path.basename(folder_path)}.mp4"
    os.chdir(folder_path)
    retval = os.getcwd()
    print(f"当前目录:{retval}")
    command = f"ffmpeg -f concat -safe 0 -i '{ts_text_path}' -c copy '{mp4_file_name}'"
    try:
        completed = subprocess.run(command, check=True, shell=True,
                                   stdout=subprocess.PIPE)
        result = completed.stdout.decode("utf-8")
        print(f"code:{completed.returncode}")
        if completed.returncode != 0:
            raise
        logger.info(f"{mp4_file_name} 合并完成！")
    except subprocess.CalledProcessError:
        logger.error(f"{mp4_file_name},转换失败")
    except Exception:
        logger.error("异常退出")


def mergeMp4(folder_path, ts_list):
    """
    folder_path 文件最外层目录
    ts_list 文件列表
    :param folder_path:
    :param ts_list:
    :return:
    """
    start_time = time.time()
    print('开始合成影片..')
    os.path.basename()

# def mergeMp4(folder_path, ts_list):
# 	# 開始時間
#     start_time = time.time()
#     print('开始合成影片..')
#
#     for i in range(len(ts_list)):
#         file = ts_list[i].split('/')[-1][0:-3] + '.mp4'
#         full_path = os.path.join(folder_path, file)
#         video_name = folder_path.split(os.path.sep)[-1]
#         if os.path.exists(full_path):
#             with open(full_path, 'rb') as f1:
#                 with open(os.path.join(folder_path, video_name + '.mp4'), 'ab') as f2:
#                     f2.write(f1.read())
#         else:
#             print(file + " 失敗 ")
#     end_time = time.time()
#     print('花費 {0:.2f} 秒合成影片'.format(end_time - start_time))
#     print('下載完成!')
