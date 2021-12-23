import unittest
from pathlib import Path


def remane_func(name: str) -> str:
    tags = True
    changed_name = name.strip()
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
    if "_" in changed_name:
        elements = changed_name.split("_")
        changed_name = " ".join(elements)

    return changed_name


class SomeVideoRenameTest(unittest.TestCase):
    def setUp(self) -> None:
        some_list = Path.cwd().joinpath("files.txt")
        some_another_list = Path.cwd().joinpath("duplicates.txt")
        with open(some_list, "r") as f:
            self.films = f.readlines()
        with open(some_another_list, "r") as f:
            self.duplicates = f.readlines()

    def test_some_splitter(self):
        for el in self.films:
            result = remane_func(el)
            print(result)

    def test_some_duplicates(self):
        for el in self.duplicates:
            result = remane_func(el)
            print(result)
