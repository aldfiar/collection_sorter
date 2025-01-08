from collections import namedtuple
from pathlib import Path
from typing import Callable, List, Union

from collection_sorter.common.files import CollectionPath

support_extension = [
    "mp3",
    "wma",
    "flac",
    ".wav",
    "mc",
    "aac",
    "m4a",
    "ape",
    "dsf",
    "dff",
]


def has_music_extension(path: Path) -> bool:
    is_extension = False
    if path.is_file():
        name = path.name
        if "." in name:
            extension = name.split(".")[1]
            return extension in support_extension

    return is_extension


MusicFile = namedtuple("MusicFile", ["file", "tag"])


class MusicCollection(CollectionPath):

    def __init__(self, path: Union[Path, str]) -> None:
        super().__init__(path)

    def get_music(self):
        all_files = self.collect_all()
        music = self._filter_by_extension(list(all_files))
        music_parsed = list()

    @classmethod
    def _filter_by_extension(cls, paths: List[Path]) -> List[Path]:
        filtered = list(filter(lambda x: has_music_extension(x), paths))
        return filtered

    @classmethod
    def get_by_tag_value(cls, files: List[Path], func: Callable):
        tag_value_map = dict()
        for file in files:
            tag = TinyTag.get(str(file))
            key = func(tag)
            if key not in tag_value_map:
                tag_value_map[key] = list()

            tag_value_map[key].append(file)

        return tag_value_map
