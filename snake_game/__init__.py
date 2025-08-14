#!/usr/bin/env python3
"""
Snake Game - A classic snake game for terminal/CLI
"""

__version__ = "1.0.1"
__author__ = "Kit_lee"
__description__ = "A classic snake game playable in terminal/CLI"

from .game import main

def cli():
    """Entry point for command line interface"""
    main()

__all__ = ['cli', 'main']