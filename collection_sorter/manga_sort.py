import logging
import shutil
from optparse import OptionParser
from pathlib import Path
from typing import List

from collection_sorter.common.sorter import BaseCollection, SortExecutor
from collection_sorter.manga.manga_sorter import MangaSorter
from collection_sorter.manga.manga import MangaParser


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
                    # For author folders mode, preserve the manga title portion
                    manga_info = MangaParser.parse(manga_dir.name)
                    manga_title = manga_dir.name.split("]")[-1].strip()
                    dest_path = author_dest / manga_title
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


