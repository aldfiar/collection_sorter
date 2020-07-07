import logging
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from collection_sorter.files import get_folders

logger = logging.getLogger('zipper')


class Zipper(object):
    @classmethod
    def zip_directory(cls, path: Path, destination: Path = None, override_name=None) -> Path:
        full_path = Path(path).expanduser().resolve(strict=True)
        if override_name:
            override_path = Path(override_name)
            name = override_name
        else:
            name = path.name

        zfn = f"{name}.zip"

        if destination:
            fzp = destination.joinpath(zfn)
        else:
            fzp = full_path.parent.joinpath(zfn)

        if fzp.exists():
            ozfp = fzp.parent.joinpath(f"{name}_previous.zip")
            fzp.rename(ozfp)

        with ZipFile(fzp, 'w', ZIP_DEFLATED) as zf:
            for file in path.iterdir():
                arc = file.relative_to(full_path.parent) if override_name is None else override_path.joinpath(file.name)
                zf.write(file, arc)
        logger.info(f"Copy files to {zfn} archive")
        return fzp

    @classmethod
    def zip_folders(cls, path: Path, zip_parent=False):
        folders = get_folders(path)
        for directory in folders:
            cls.zip_directory(directory)
        if zip_parent:
            cls.zip_directory(path)
        logger.info(f"Zip {len(folders)} folders")
