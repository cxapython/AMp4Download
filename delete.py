import os

def delete_mp4(folder_path):
    files = os.listdir(folder_path)
    originFile = folder_path.split(os.path.sep)[-1] + '.mp4'
    for file in files:
        if file != originFile:
            os.remove(os.path.join(folder_path, file))


def delete_m3u8(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        if file.endswith('.m3u8'):
            os.remove(os.path.join(folder_path, file))
