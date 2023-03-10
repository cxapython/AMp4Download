import os
import shutil

def delete_mp4(folder_path):
    print("开始删除ts文件")
    shutil.rmtree(folder_path)
    print (f"删除成功:{folder_path}")
def delete_m3u8(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith('.m3u8'):
            os.remove(os.path.join(folder_path, file))
