"""
Package for ingesting dictionary data into python classes.
"""

__all__ = [
    "from_dict",
    "table_to_item",
    "table_to_items",
    "typecast",
    "Path",
    "default_convertor",
    "Route",
    "Chart",
]
from .serdes import from_dict, typecast, table_to_item, table_to_items
from .routes import Path, Route, Chart
from .converter import default_convertor
