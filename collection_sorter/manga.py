import logging
import re
from pathlib import Path
from typing import Dict, Any, List

from collection_sorter.files import get_folders

logger = logging.getLogger('manga')
brackets = {"(", ")", "[", "]", "{", "}"}


class MangaExtractor(object):

    def extract(self, path: Path) -> Dict[str, Any]:
        result = dict()
        if path.is_file():
            logger.error(f"Need folder for parsing. {path} is a file")
        else:
            # if linux
            filename = path.name.replace("_", " ")
            author_data = self._extract_author_string(filename)
            if author_data:
                result.update(**author_data)

            name_data = self._extract_name(filename)
            if name_data:
                result.update(**name_data)
            if not result:
                folders = get_folders(path)
                if folders:
                    # treat as author folder with manga inside
                    result["author"] = filename
                else:
                    # treat as folder with manga
                    result["name"] = filename

        updated = {k: v.strip() if isinstance(v, str) else v for k, v in result.items()}
        return updated

    def _extract_author_string(self, filename: str) -> Dict[str, str]:
        info = dict()
        bfi = filename.find("[")
        bli = filename.find("]")
        if bli == -1 and bfi == -1:
            return info

        author_info = filename[bfi + 1:bli]

        result = re.search(r"(.+)\s?_?\((.+)\)", author_info)
        if result:
            info["group"] = result.group(1)
            author = result.group(2)
            if "," in author:
                authors = [x.strip() for x in author.split(",")]
                author = ",".join(authors)
            info["author"] = author.strip()
        else:
            info["author"] = author_info.strip()
        return info

    def extract_author_info(self, filename: str) -> str:
        info = self._extract_author_string(filename)
        author = info["author"]
        group = info["group"]
        return f"{group} ({author})" if group is not None else f"{author}"

    def _extract_tags(self, tag_string: str) -> List[str]:
        tags = list()
        fi = 0
        li = 0
        index = 0
        last = False
        first = False
        for letter in tag_string:
            if letter in brackets:
                if not first:
                    first = True
                    fi = index
                else:
                    last = True
                    li = index
            if last:
                tag = tag_string[fi + 1: li]
                tags.append(tag.strip())
                last = False
                first = False

            index += 1

        return tags

    def _extract_name(self, filename: str) -> Dict[str, Any]:
        info = dict()
        bli = filename.find("]")
        if bli == -1:
            return info

        name_without_author = filename[bli + 1:]

        result = re.search(r"[\w\d_  !~'\\-]+", name_without_author)
        if result:
            name = result.group(0)
            index = name_without_author.find(name)
            tag_string = name_without_author[index + len(name):]
            tags = self._extract_tags(tag_string)
            info["tags"] = tags
            info["name"] = name.strip()
        else:
            info["name"] = name_without_author.strip()

        return info

    def extract_name(self, filename: str, keep_tags=True) -> str:
        # search for author end bracket
        info = self._extract_name(filename)
        name = info["name"]
        if keep_tags and info["tags"]:
            tag_values = " ".join(map(lambda x: "[{value}]".format(value=x), info["tags"]))
            name = f"{name} {tag_values}"

        return name

    def extract_group(self, filename: str) -> str:
        info = self._extract_author_string(filename)
        return info.get("group")

    def extract_author(self, filename: str) -> str:
        info = self._extract_author_string(filename)
        return info["author"]
