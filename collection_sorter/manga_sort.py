import logging
import shutil
from optparse import OptionParser
from pathlib import Path
from typing import List

from common.sorter import BaseCollection, SortExecutor
from manga.manga_sorter import MangaSorter
from manga.manga import MangaParser


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
    parser.add_option(
        "--author-folders",
        help="Process folders as author collections",
        dest="author_folders",
        action="store_true"
    )

    options, args = parser.parse_args()

    return options, args


def manga_sort(source: List[str], destination: str, archive: bool, move: bool, author_folders: bool = False):
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
    
    task = MangaSorter(archive=archive, remove=move, author_folders=author_folders)
    
    for src in source:
        src_path = Path(src)
        if not src_path.exists():
            logging.warning(f"Source path does not exist: {src}")
            continue
            
        if author_folders:
            # Process as author folder containing multiple manga
            author_name = src_path.name
            author_dest = dest_path / author_name
            author_dest.mkdir(parents=True, exist_ok=True)
            
            # Process each subfolder as a manga, preserving original names
            collection = BaseCollection(src_path)
            for manga_dir in collection.get_folders():
                if manga_dir.is_dir():
                    # Extract manga name from directory name, preserving original structure
                    manga_info = MangaParser.parse(manga_dir.name)
                    manga_name = manga_info["name"]
                    # Remove any leading/trailing spaces and normalize internal spaces
                    manga_name = " ".join(manga_name.split())
                    dest_path = author_dest / manga_name
                    if archive:
                        task.execute(manga_dir, author_dest)
                    else:
                        if move:
                            shutil.move(str(manga_dir), str(dest_path))
                        else:
                            shutil.copytree(str(manga_dir), str(dest_path))
        else:
            # Process normally as individual manga folders
            task.execute(src_path, dest_path)


