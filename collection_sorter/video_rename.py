import logging
import uuid
import re
from optparse import OptionParser
from pathlib import Path
from typing import List

from .common.sorter import SortExecutor, BaseCollection, MultiThreadTask


def rename_sort_options():
    usage = "%prog -d destination source1 source 2"
    parser = OptionParser(usage=usage)
    options, args = parser.parse_args()

    return options, args


def rename_sort(source: List[str]):
    logging.info(f"Get source: {source}")
    sorter = SortExecutor()
    task = SomeStrange()
    for element in source:
        collection = BaseCollection(element)
        sorter.sort(collection=collection, task=task)


def rename_video():
    options, args = rename_sort_options()
    rename_sort(args)


def rename_function(name: str) -> str:
    tags = True
    changed_name = name.strip()
    extension = changed_name.split(".")[-1]
    changed_name = changed_name.replace(extension, "")
    while tags:
        start = changed_name.find("[")
        end = changed_name.find("]")
        brackets = end != -1 and start != -1
        if brackets:
            if start == 0:
                changed_name = changed_name[end + 1:]
            else:
                changed_name = changed_name[:start - 1] + changed_name[end + 1:]
        another_start = changed_name.find("(")
        another_end = changed_name.find(")")
        curve = another_start != -1 and another_end != -1
        if curve:
            if another_start == 0:
                changed_name = changed_name[another_end + 1:]
            else:
                changed_name = changed_name[:another_start - 1] + changed_name[another_end + 1:]
        tags = curve or brackets
        changed_name = changed_name.strip()


    elements = re.split("_| ", changed_name)
    # for element in elements:
    #     if " " in element:
    #         res = element.split(" ")
    #         final_elements.extend(res)
    #     else:
    #         final_elements.append(element)

    final_elements = list(filter(None, elements))

    full_name = "_".join(final_elements)
    if full_name.endswith("."):
        result = f"{full_name}{extension}"
    else:
        result = f"{full_name}.{extension}"
    return result


class SomeStrange(MultiThreadTask):
    def __init__(self, template=None, archive=False, replace_function=None, remove=False) -> None:
        super().__init__()
        self._template = template
        self._archive = archive
        self._replace_function = replace_function
        self._remove = remove

    def execute(self, source: Path, destination: Path = None):
        collection = BaseCollection(source)

        root_name = source.name
        info = {'root': root_name}
        files = collection.collect_all()

        def rename_closure(path: Path):
            name = path.name
            changed = rename_function(name)
            renamed_path = path.parent.joinpath(changed)
            if renamed_path != path:
                if renamed_path.exists():
                    duplicate_name = f"duplicate_{uuid.uuid4()}_" + changed
                    renamed_path = path.parent.joinpath(duplicate_name)
                path.rename(renamed_path)
                logging.info(f"Change {name} to {renamed_path}")

            return renamed_path

        result = list(map(rename_closure, files))
        print(result)


if __name__ == "__main__":
    rename_video()
