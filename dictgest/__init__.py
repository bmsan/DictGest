"""
Package for ingesting dictionary data into python classes.
"""

__all__ = ["from_dict", "typecast", "Path", "default_convertor"]
from .serdes import from_dict, typecast, Path
from .converter import default_convertor
