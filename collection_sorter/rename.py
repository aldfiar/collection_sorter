import logging
from pathlib import Path

logger = logging.getLogger('rename')


class LinuxRename(object):
    @classmethod
    def rename(self, path: Path):
        new_path = None
        if not path.is_file():
            logger.warning("Don't rename directories")
        else:
            name = path.name
            linux_name = name.replace(" ", "_")
            new_path = path.parent.joinpath(linux_name)
            logger.debug(f'New name for file {path} to {new_path}')

        return new_path
