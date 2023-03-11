import requests
import os
from bs4 import BeautifulSoup


def get_cover(html_file, folder_path):
  # get cover
  soup = BeautifulSoup(html_file.text, "html.parser")
  cover_name = f"{folder_path.name}.jpg"
  cover_path = folder_path / cover_name
  for meta in soup.find_all("meta"):
      meta_content = meta.get("content")
      if not meta_content:
          continue
      if "preview.jpg" not in meta_content:
          continue
      try:
          r = requests.get(meta_content)
          with cover_path.open("wb") as cover_fh:
              r.raw.decode_content = True
              for chunk in r.iter_content(chunk_size=1024):
                  if chunk:
                      cover_fh.write(chunk)
          print(f"cover downloaded as {cover_name}")

      except Exception as e:
          print(f"unable to download cover: {e}")

