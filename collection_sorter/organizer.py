import logging
import os
import shutil
from base64 import b64encode
from pathlib import Path
from typing import Any, Dict

from parse import *

from collection_sorter.common.sorter import BaseCollection, MultiThreadTask

logger = logging.getLogger("collection_renamer")


def file_name_parser(name: str):
    search("{:I}", name)


def produce_amount_keys(amount_of_keys):
    random_bytes = os.urandom(amount_of_keys)
    token = b64encode(random_bytes).decode("utf-8")
    return token


def sort_template(info: Dict[str, Any], symbol_replace_function=None):
    author = info["author"]
    group = info.get("group")
    name = " ".join(info["name"].split())
    language_tag = None
    if "tags" in info:
        for tag in info["tags"]:
            if tag.title() in languages:
                language_tag = tag
    author_info = f"[{group} ({author})]" if group is not None else f"[{author}]"

    template = (
        f"{author_info} {name}"
        if language_tag is None
        else f"{author_info} {name} [{language_tag}]"
    )

    if symbol_replace_function:
        template = symbol_replace_function(template)
    return template


# def collection_function():


class CollectionSorter(MultiThreadTask):
    def __init__(
        self, template=sort_template, archive=False, replace_function=None, remove=False
    ) -> None:
        super().__init__()
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._remove = remove

    def _to_destination(self, source: Path, destination: Path):
        collection = BaseCollection(source)

        root_name = source.name

        if self._archive:
            if destination:
                archive = collection.archive_directory(
                    destination=destination, new_name=root_name
                )
                if archive.exists() and self._remove:
                    collection.delete()
        else:
            if destination:
                if self._remove:
                    collection.copy(destination)
                else:
                    collection.move(destination)

    def execute(self, source: Path, destination: Path = None):
        collection = BaseCollection(source)

        root_name = source.name
        info = {"root": root_name}

        def rename_function(path: Path):
            name = collection.path.name
            search("{:l}", name)

            new_name = self._template(path=path, directory=destination)
            file_destination = source.joinpath()
            shutil.move(source, file_destination)

        collection.map(rename_function)
