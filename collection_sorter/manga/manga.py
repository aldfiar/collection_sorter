import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("manga")
brackets = {"(", ")", "[", "]", "{", "}"}


class MangaParser(object):
    @staticmethod
    def _extract_tags(tag_string: str) -> List[str]:
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
                tag = tag_string[fi + 1 : li]
                tags.append(tag.strip())
                last = False
                first = False

            index += 1

        return tags

    @staticmethod
    def _extract_author_string(author_data: str) -> Tuple[str, str]:
        group = None
        result = re.search(r"(.+)\s?_?\((.+)\)", author_data)
        if result:
            group = result.group(1).strip()
            author = result.group(2)
            if "," in author:
                authors = [x.strip() for x in author.split(",")]
                author = ",".join(authors)
            author = author.strip()
        else:
            author = author_data.strip()

        if "." in author:
            author = author.replace(".", "")

        return author, group

    @staticmethod
    def _extract_data(manga_data: str) -> Tuple[str, List[str]]:
        tags = []
        result = re.search(r"[\w\d_  !~'\\-]+", manga_data)
        if result:
            manga_name = result.group(0)
            index = manga_data.find(manga_name)
            tag_string = manga_data[index + len(manga_name) :]
            tags = MangaParser._extract_tags(tag_string)
            name = manga_name.strip()
        else:
            name = manga_data.strip()

        return name, tags

    @staticmethod
    def _monthly_manga(name: str) -> str:
        index = 0
        find_digit = False
        for character in name:
            if character.isdigit():
                find_digit = True
                break
            index += 1
        if find_digit:
            author = name[0 : index - 1]
        else:
            author = name

        return author.strip()

    @staticmethod
    def parse(filename) -> Dict[str, Any]:
        parsed = {}
        info_at_start = False

        info_tag_start = filename.find("(")
        info_tag_end = filename.find(")")
        if info_tag_end != -1 and info_tag_start == 0:
            info_at_start = True

        author_tag_start = filename.find("[")
        author_tag_end = filename.find("]")
        is_found = author_tag_end != -1 and author_tag_start != -1
        author_at_start = author_tag_start == 0 or (
            info_at_start and author_tag_start - info_tag_end <= 2
        )
        if is_found and author_at_start:
            author_data = filename[author_tag_start + 1 : author_tag_end].strip()
            author, group = MangaParser._extract_author_string(author_data)
            parsed["author"] = author
            parsed["group"] = group
            manga_data = filename[author_tag_end + 1 :]
        else:
            manga_data = filename

        name, tags = MangaParser._extract_data(manga_data)
        parsed["name"] = name
        parsed["tags"] = tags

        if "author" not in parsed:
            author = MangaParser._monthly_manga(name)
            parsed["author"] = author

        return parsed
