import logging
import uuid
from optparse import OptionParser
from pathlib import Path
from typing import List

from .common.sorter import BaseCollection, MultiThreadTask, SortExecutor


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


def rename_main():
    options, args = rename_sort_options()
    rename_sort(args)


class SomeStrange(MultiThreadTask):
    def __init__(
        self, template=None, archive=False, replace_function=None, remove=False
    ) -> None:
        super().__init__()
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._remove = remove

    def execute(self, source: Path, destination: Path = None):
        collection = BaseCollection(source)

        root_name = source.name
        info = {"root": root_name}
        files = collection.collect_all()

        def rename_function(path: Path):
            name = path.name

            if ".." in name:
                # logging.info(name)
                result = name.replace("..", ".")
                renamed = path.parent.joinpath(result)
                new_path = path.rename(renamed)
                return new_path
            if all([c.isdigit() for c in name.split(".")[0]]):
                parent = path.parent
                identificator = uuid.uuid4()
                new_name = f"{parent.name}_{identificator}"
                res = path.parent.joinpath(new_name)
                result = path.rename(res)
                return result

        result = list(map(rename_function, files))
        print(result)


if __name__ == "__main__":
    rename_main()
