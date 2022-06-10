from datetime import datetime
from typing import Mapping, TypeVar
from dateutil import parser as date_parser
from dictgest.cast import TypeConvertor


T = TypeVar("T")


class Convertor(Mapping):
    """
    Used to convert data to certain datatypes.
    Conversion mappings need to be registered using the `register` method
    """

    def __init__(self):
        self.mappings: dict[type, TypeConvertor] = {}

    def register(self, dtype: type[T], converter: TypeConvertor[T]):
        """Registers a convertor for a data type

        Parameters
        ----------
        dtype
            Data type for which to use convertor
        converter
            Callable capable of converting data to dtype
        """

        self.mappings[dtype] = converter

    def __getitem__(self, key):
        return self.mappings[key]

    def get_converter(self, key):
        """Return registered conversion for key type.
        If no conversion is registred, return the last resort convertor (the type constructor)
        """
        return self[key] if key in self else key

    def __contains__(self, key):
        return key in self.mappings

    def __len__(self):
        return len(self.mappings)

    def __iter__(self):
        yield from self.mappings


def bool_converter(val) -> bool:
    """Convert to bool"""
    if isinstance(val, bool):
        return val
    if val == 1:
        return True
    if val == 0:
        return False
    if isinstance(val, str):
        lower = val.lower().strip()
        if lower in ["true", "yes", "ok"]:
            return True
        if lower in ["false", "no"]:
            return False
    raise ValueError(f"Unable to convert [{val}] to bool")


def date_convertor(val) -> datetime:
    """Convert value to datetime.
    If the input is numeric it will be treated as unixtime.
    If the input is a string the format will be autodeduced
    """
    if isinstance(val, datetime):
        return val
    try:
        val = float(val)
        return datetime.utcfromtimestamp(val)
    except ValueError:
        pass

    return date_parser.parse(val)


default_convertor = Convertor()

default_convertor.register(datetime, date_convertor)
default_convertor.register(bool, bool_converter)
