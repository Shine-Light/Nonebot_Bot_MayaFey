import requests
from pathlib import Path
from utils import url
import ujson as json


class DownloadError(Exception):
    pass


def get_preset_config(file_path: Path) -> None:
    data = requests.get(url.morning_config).json()
    if data:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        raise DownloadError
