import os
import subprocess
import time

from loguru import logger


# merge_ts_file(folder_path, ts_list[:])
def merge_ts_file(folder_path, ts_list):
        merge_text_path = os.path.join(folder_path, f"{int(time.time())}_merge_file.txt")
        with open(merge_text_path, "w+") as f:
            for index, ts_url in enumerate(ts_list):
                file = os.path.basename(ts_url)
                content = f"file '{file}'\n"
                if index == len(ts_list) - 1:
                    content = f"file '{file}'"
                f.write(content)
        return merge_text_path


# folder_path, ts_text_path
def merge_mp4_file(temp_path,folder_path, ts_text_path):
    mp4_file_name =f"{os.path.basename(folder_path)}.mp4"
    os.chdir(folder_path)
    retval = os.getcwd()
    print(f"当前目录:{retval}")
    command = f"ffmpeg -f concat -safe 0 -i '{ts_text_path}' -c copy '{mp4_file_name}'"
    try:
        completed = subprocess.run(command, check=True, shell=True,
                                   stdout=subprocess.PIPE)
        result = completed.stdout.decode("utf-8")
        logger.info(f"code:{completed.returncode}")
        if completed.returncode != 0:
            raise
        logger.info(f"{mp4_file_name} 合并完成！")
    except subprocess.CalledProcessError:
        logger.error(f"{mp4_file_name},转换失败")
    except Exception:
        logger.error("异常退出")
if __name__=="__main__":
    from delete import delete_mp4
    ff="/sdcard/av/lulu-184"
    ts="1677847845_merge_file.txt"
    merge_mp4_file(ff,ts)
    delete_mp4(ff)
