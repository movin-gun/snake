"""Snake Game - a classic snake game for the terminal."""

__version__ = "3.0.0"
__author__ = "Kit Lee"


def cli():
    """Console-script entry point."""
    import sys
    from .game import main
    sys.exit(main())


def main(argv=None):
    from .game import main as _main
    return _main(argv)


__all__ = ["cli", "main", "__version__"]
