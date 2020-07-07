import argparse
import logging
from pathlib import Path

from collection_sorter.manga import logger
from collection_sorter.manga_sorter import MangaSorter
from collection_sorter.templates import base_manga_template

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Sort collection')
    parser.add_argument('source', type=str,
                        help='Source path')
    parser.add_argument('destination', type=str,
                        help='Destination path')
    parser.add_argument('--zip', help='Zip files', action="store_true")
    parser.add_argument('--move', help='Remove from source', action="store_true")

    args = parser.parse_args()
    logger.info(f"Get source: {args.source}, destination: {args.destination}")
    sorter = MangaSorter()
    sorter.sort(Path(args.source), Path(args.destination), template_function=base_manga_template, zip_files=args.zip,
                remove_original=args.move)
