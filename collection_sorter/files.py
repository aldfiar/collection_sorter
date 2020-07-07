import os
from os.path import isdir
from pathlib import Path
from typing import List


def get_folders(path: Path) -> List[Path]:
    paths = [f for f in path.iterdir() if f.is_dir()]
    return paths


def get_content(path: Path) -> List[Path]:
    paths = [f for f in path.iterdir()]
    return paths
