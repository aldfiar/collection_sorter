import logging
import uuid
import re
from optparse import OptionParser
from pathlib import Path
from typing import List

from .common.sorter import SortExecutor, BaseCollection, MultiThreadTask


def rename_sort_options():
    usage = "%prog -d destination source1 source 2"
    parser = OptionParser(usage=usage)
    options, args = parser.parse_args()

    return options, args


def rename_sort(source: List[str]):
    logging.info(f"Get source: {source}")
    sorter = SortExecutor()
    task = SomeStrange()
    for element in source:
        collection = BaseCollection(element)
        sorter.sort(collection=collection, task=task)


def rename_video():
    options, args = rename_sort_options()
    rename_sort(args)


def remove_brackets(filename):
    result = ''
    inside_brackets = 0

    for char in filename:
        if char in '([':
            inside_brackets += 1
        elif char in ')]':
            inside_brackets -= 1
        elif inside_brackets == 0:
            result += char

    return result


def rename_function(filename):
    splited = filename.split('.')
    extension = splited[-1]
    name = splited[0].replace("-", "")
    if "@" in name:
        name = name.split("@")[-1]
    brackets_removed = remove_brackets(name)
    name_parts = re.split("_| ", brackets_removed)

    title = ''
    episode = ''

    for part in name_parts:
        if part.isdigit():
            episode = part
            break
        else:
            title += part + ' '
    updated = title.strip()
    if episode:
        result = f"{updated} - {episode}.{extension}"
    else:
        result = f"{updated}.{extension}"
    return result


class SomeStrange(MultiThreadTask):
    def __init__(self, template=None, archive=False, replace_function=None, remove=False) -> None:
        super().__init__()
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._remove = remove

    def execute(self, source: Path, destination: Path = None):
        collection = BaseCollection(source)

        root_name = source.name
        info = {'root': root_name}
        files = collection.collect_all()

        def rename_closure(path: Path):
            name = path.name
            changed = rename_function(name)
            renamed_path = path.parent.joinpath(changed)
            if renamed_path != path:
                if renamed_path.exists():
                    duplicate_name = f"duplicate_{uuid.uuid4()}_" + changed
                    renamed_path = path.parent.joinpath(duplicate_name)
                print(renamed_path)
                path.rename(renamed_path)
                logging.info(f"Change {name} to {renamed_path}")

            return renamed_path

        result = list(map(rename_closure, files))
        print(result)


if __name__ == "__main__":
    rename_video()
