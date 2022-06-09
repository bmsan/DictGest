"""
Package for ingesting dictionary data into python classes.
"""

__all__ = ["from_dict", "typecast", "Path", "default_convertor", "Route", "Chart"]
from .serdes import from_dict, typecast
from .routes import Path, Route, Chart
from .converter import default_convertor
