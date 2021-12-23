import logging
import uuid
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from collection_sorter.common.files import CollectionPath

logger = logging.getLogger('archive')


class ArchivedCollection(CollectionPath):

    def is_archive(self):
        return self._path.exists() and self._path.is_file()

    def archive_directory(self, destination: Path = None, new_name=None) -> 'ArchivedCollection':
        if new_name:
            override_path = Path(new_name)
            name = new_name
        else:
            name = self._path.name

        zfn = f"{name}.zip"

        if destination:
            fzp = destination.joinpath(zfn)
        else:
            fzp = self._path.parent.joinpath(zfn)

        if fzp.exists():
            identifier = str(uuid.uuid4())
            ozfp = fzp.parent.joinpath(f"{name}_duplicate_{identifier}.zip")
            fzp.rename(ozfp)

        with ZipFile(fzp, 'w', ZIP_DEFLATED) as zf:
            for file in self._path.iterdir():
                arc = file.relative_to(self._path.parent) if new_name is None else override_path.joinpath(file.name)
                zf.write(file, arc)

        logger.info(f"Copy files from: {self._path} to {zfn} archive")

        return ArchivedCollection(fzp)

    def exists(self):
        return self._path.exists() and self._path.stat().st_size > 0

    def archive_folders(self, zip_parent=False) -> 'ArchivedCollection':
        folders = self.get_folders()
        for directory in folders:
            self.archive_directory(directory)
        if zip_parent:
            self.archive_directory(self._path.parent)

        logger.info(f"Zip {len(folders)} folders in {self._path}")

        return self
