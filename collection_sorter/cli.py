import argparse
import logging
from pathlib import Path
from typing import List

from collection_sorter.manga_sort import manga_sort
from collection_sorter.mass_rename import rename_sort
from collection_sorter.mass_zip import zip_collections
from collection_sorter.video_rename import rename_sort as video_rename_sort

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_parser():
    parser = argparse.ArgumentParser(
        description='Collection Sorter - Organize and process various file collections'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Manga sort command
    manga_parser = subparsers.add_parser('manga', help='Sort manga collections')
    manga_parser.add_argument('sources', nargs='+', help='Source directories')
    manga_parser.add_argument('-d', '--destination', help='Destination directory')
    manga_parser.add_argument('-a', '--archive', action='store_true', help='Create archives')
    manga_parser.add_argument('-m', '--move', action='store_true', help='Remove source after processing')
    
    # Mass rename command
    rename_parser = subparsers.add_parser('rename', help='Batch rename files')
    rename_parser.add_argument('sources', nargs='+', help='Source directories')
    rename_parser.add_argument('-d', '--destination', help='Destination directory')
    rename_parser.add_argument('-a', '--archive', action='store_true', help='Create archives')
    rename_parser.add_argument('-m', '--move', action='store_true', help='Remove source after processing')
    
    # Mass zip command
    zip_parser = subparsers.add_parser('zip', help='Create archives from collections')
    zip_parser.add_argument('sources', nargs='+', help='Source directories')
    zip_parser.add_argument('-d', '--destination', help='Destination directory')
    zip_parser.add_argument('-a', '--archive', action='store_true', help='Create archives')
    zip_parser.add_argument('-m', '--move', action='store_true', help='Remove source after processing')
    
    # Video rename command
    video_parser = subparsers.add_parser('video', help='Rename video files')
    video_parser.add_argument('sources', nargs='+', help='Source directories')
    video_parser.add_argument('-d', '--destination', help='Destination directory')
    
    return parser

def main():
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'manga':
            manga_sort(
                source=args.sources,
                destination=args.destination,
                archive=args.archive,
                move=args.move
            )
        
        elif args.command == 'rename':
            rename_sort(
                source=args.sources,
                destination=args.destination,
                archive=args.archive,
                move=args.move
            )
        
        elif args.command == 'zip':
            zip_collections(
                source=args.sources,
                destination=args.destination,
                archive=args.archive,
                move=args.move
            )
        
        elif args.command == 'video':
            video_rename_sort(
                source=args.sources,
                destination=args.destination
            )
            
    except Exception as e:
        logging.error(f"Error processing command {args.command}: {str(e)}")
        raise

if __name__ == '__main__':
    main()
