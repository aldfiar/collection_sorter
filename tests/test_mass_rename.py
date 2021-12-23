import os
import re
from base64 import b64encode
from unittest import TestCase

from parse import search

ex = ["2B_-_Nier_Automata__3_072", "Asuka_1556", "DSC_0312", "6 - rys8Pdi", "h-VjAdUN8CI", "Канан_белье_full_586",
      "10_257", "023", "EqKgvPDUYAIdcQz", "Photo 143", "Photo_123"]


def check_word(words):
    res = []
    for word in words:
        if len(word) > 1:
            r = search("{:d}{:l}", word)
            if not r:
               res.append(word)
    print(res)


class TestMassRename(TestCase):
    def test_parser(self):
        for el in ex:
            res = re.split(" |_|-", el)
            f = list(filter(lambda x: not x.isdigit() and x, res))
            check_word(f)
