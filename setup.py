#!/usr/bin/env python3
"""
Setup script for Snake Game
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name="kitsnakegame",
    version="2.1.0",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    description="A classic snake game for terminal/CLI",
    long_description="A classic snake game that runs in your terminal. Features multiple difficulty levels, intuitive controls, and a retro ASCII art interface.",
    long_description_content_type="text/plain",
    url="https://github.com/anthropics/snake-game-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment :: Arcade",
        "Topic :: Terminals",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - uses only Python standard library
    ],
    entry_points={
        "console_scripts": [
            "snakegame=snake_game:cli",
            "snake-game=snake_game:cli",
            "snake=snake_game:cli",
        ],
    },
    keywords=["game", "snake", "terminal", "cli", "arcade", "retro"],
    project_urls={
        "Bug Reports": "https://github.com/anthropics/snake-game-cli/issues",
        "Source": "https://github.com/anthropics/snake-game-cli",
    },
)