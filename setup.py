#!/usr/bin/env python
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

try:
    from setuptools import setup, find_packages
except ImportError:
    from setuptools import setup, find_packages

setup(
    name='collection_sorter',
    version='0.0.1',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators"
    ],
    packages=find_packages(),

    install_requires=[
        "pycountry>=20.7.3",
        "parse>=1.19.0",
        "click>=7.1.2",
        "python-dateutil>=2.1"
    ],
    entry_points={
        'console_scripts': [
            'mangasort = collection_sorter:manga_sort_main',
            'collection_sort = collection_sorter:mass_rename_main',
        ]
    },
    tests_require=['pytest'],
    zip_safe=True
)
