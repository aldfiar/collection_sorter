#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from setuptools import setup, find_packages

setup(
    name='collection_sorter',
    version='0.1.1',
    description='A command-line tool for organizing and processing various file collections',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    install_requires=[
        "pycountry>=23.12.11",
        "parse>=1.20.1",
        "click>=8.1.7",
        "python-dateutil>=2.9.0",
        "rich>=13.7.0",
        "tqdm>=4.66.1",
        "pyyaml>=6.0.1",
        "pydantic>=2.6.1",
        "tomli>=2.0.1"
    ],
    entry_points={
        'console_scripts': [
            'collection-sorter = collection_sorter.cli:main',
        ]
    },
    python_requires='>=3.9',
    tests_require=['pytest'],
    zip_safe=True
)
