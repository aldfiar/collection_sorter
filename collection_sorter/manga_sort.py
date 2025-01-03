import logging
from optparse import OptionParser
from pathlib import Path
from typing import List

from common.sorter import BaseCollection, SortExecutor
from manga.manga_sorter import MangaSorter


def manga_sort_options():
    usage = "%prog -d destination  source1 source 2"
    parser = OptionParser(usage=usage)
    parser.add_option('-a', "--archive", help='Zip files', dest="archive", action="store_true")
    parser.add_option('-m', "--move", help='Remove from source', dest="move", action="store_true")
    parser.add_option('-d', "--destination", help='Destination folder', dest="destination", default=None)

    options, args = parser.parse_args()

    return options, args


def manga_sort(source: List[str], destination: str, archive: bool, move: bool):
    logging.info(f"Get source: {source}, destination: {destination}")
    task = MangaSorter(archive=archive, remove=move)
    sorter = SortExecutor()
    for element in source:
        root = Path(element)
        collection = BaseCollection(root)
        sorter.sort(collection=collection, destination=destination, task=task)


def manga_sort_main():
    options, args = manga_sort_options()
    manga_sort(args, options.destination, options.archive, options.move)


if __name__ == "__main__":
    manga_sort_main()
