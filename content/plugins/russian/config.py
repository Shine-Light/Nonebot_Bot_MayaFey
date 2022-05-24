from typing import Tuple
from pydantic import BaseModel, Extra
from pathlib import Path
from utils import path


class Config(BaseModel, extra=Extra.ignore):
    max_bet_gold: int = 1000
    sign_gold: Tuple[int, int] = (1, 100)
    russian_path: Path = path.russian_path
