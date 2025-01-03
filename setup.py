#!/usr/bin/env python

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
