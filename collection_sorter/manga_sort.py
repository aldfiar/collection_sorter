import logging
from optparse import OptionParser
from pathlib import Path
from typing import List

from common.sorter import BaseCollection, SortExecutor
from manga.manga_sorter import MangaSorter


def manga_sort_options():
    usage = "%prog -d destination  source1 source 2"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-a", "--archive", help="Zip files", dest="archive", action="store_true"
    )
    parser.add_option(
        "-m", "--move", help="Remove from source", dest="move", action="store_true"
    )
    parser.add_option(
        "-d",
        "--destination",
        help="Destination folder",
        dest="destination",
        default=None,
    )

    options, args = parser.parse_args()

    return options, args


def manga_sort(source: List[str], destination: str, archive: bool, move: bool):
    """Sort manga files from source directories into destination.
    
    Args:
        source: List of source directory paths
        destination: Destination directory path
        archive: Whether to create archives
        move: Whether to remove source files
    """
    logging.info(f"Get source: {source}, destination: {destination}")
    
    # Create destination directory if it doesn't exist
    dest_path = Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    task = MangaSorter(archive=archive, remove=move)
    
    for src in source:
        src_path = Path(src)
        if not src_path.exists():
            logging.warning(f"Source path does not exist: {src}")
            continue
            
        task.execute(src_path, dest_path)


