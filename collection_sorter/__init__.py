import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

from .manga_sort import *
from .mass_rename import *
from .video_rename import *