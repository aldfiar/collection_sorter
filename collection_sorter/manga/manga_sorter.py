import logging
from pathlib import Path

from collection_sorter.common.sorter import BaseCollection, MultiThreadTask

from .manga import MangaParser
from .manga_template import manga_template_function

logger = logging.getLogger("manga_sorter")


class MangaCollection(BaseCollection):
    pass


class MangaSorter(MultiThreadTask):

    def __init__(
        self,
        template=manga_template_function,
        archive=False,
        replace_function=None,
        parser=MangaParser,
        remove=False,
    ) -> None:
        super().__init__()
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._parser = parser
        self._remove = remove

    def execute(self, source: Path, destination: Path):
        collection = MangaCollection(source)

        manga_info = self._parser.parse(source.name)

        new_root = manga_info["author"]
        manga_destination = destination.joinpath(new_root)
        with self._lock:
            if not manga_destination.exists():
                manga_destination.mkdir()

        directories = collection.get_folders()
        if directories:
            for directory in directories:
                updated = dict()
                updated.update(**manga_info)
                updated["name"] = directory.name
                new_name = self._template(
                    updated, symbol_replace_function=self._replace_function
                )
                self._directory_action(
                    name=new_name,
                    collection=collection,
                    destination=manga_destination,
                )
        else:
            new_name = self._template(
                manga_info, symbol_replace_function=self._replace_function
            )
            self._directory_action(
                name=new_name,
                collection=collection,
                destination=manga_destination,
            )

    def _directory_action(
        self, name: str, collection: MangaCollection, destination: Path
    ):
        logger.info(f"Change collection: {collection}")

        try:
            if self._archive:
                archive = collection.archive_directory(
                    destination=destination, new_name=name
                )
                if archive.exists() and self._remove:
                    collection.delete()
            else:
                file_destination = destination.joinpath(name)
                if self._remove:
                    collection.move(file_destination)
                else:
                    collection.copy(file_destination)
        except Exception as e:
            logger.error("Directory action failed with: {}".format(e))
