#!/usr/bin/env python3
import os
import re

from setuptools import find_packages, setup

HERE = os.path.dirname(os.path.abspath(__file__))


def read(*parts):
    with open(os.path.join(HERE, *parts), encoding="utf-8") as f:
        return f.read()


# Single source of truth for the version: snake_game/__init__.py
VERSION = re.search(r'^__version__ = "([^"]+)"', read("snake_game", "__init__.py"), re.M).group(1)

setup(
    name="kitsnakegame",
    version=VERSION,
    author="Kit Lee",
    description="A classic snake game for the terminal - no dependencies",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/movin-gun/snake",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "snakegame=snake_game:cli",
            "snake-game=snake_game:cli",
            "snake=snake_game:cli",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment :: Arcade",
    ],
    keywords=["game", "snake", "terminal", "cli", "arcade", "retro"],
    project_urls={
        "Bug Reports": "https://github.com/movin-gun/snake/issues",
        "Source": "https://github.com/movin-gun/snake",
    },
)
