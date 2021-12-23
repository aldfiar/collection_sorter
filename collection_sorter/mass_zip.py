import logging
from optparse import OptionParser
from pathlib import Path
from typing import List

from collection_sorter import MultiThreadTask, BaseCollection, SortExecutor


def zip_sort_options():
    usage = "%prog -d destination  source1 source 2"
    parser = OptionParser(usage=usage)
    parser.add_option('-a', "--archive", help='Zip files', dest="archive", action="store_true")
    parser.add_option('-m', "--move", help='Remove from source', dest="move", action="store_true")
    parser.add_option('-d', "--destination", help='Destination folder', dest="destination", default=None)

    options, args = parser.parse_args()

    return options, args


class ZipCollections(MultiThreadTask):
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
        collection = collection.archive_folders(zip_parent=True)


def zip_collections(source: List[str], destination: str, archive: bool, move: bool):
    logging.info(f"Get source: {source}, destination: {destination}")
    task = ZipCollections(archive=archive, remove=move)
    sorter = SortExecutor()
    for element in source:
        root = Path(element)
        collection = BaseCollection(root)
        sorter.sort(collection=collection, destination=destination, task=task)


def manga_sort_main():
    options, args = zip_sort_options()
    zip_collections(args, options.destination, options.archive, options.move)


if __name__ == "__main__":
    manga_sort_main()
