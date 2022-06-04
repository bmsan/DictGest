from datetime import datetime
from typing import Mapping, TypeVar
from dictgest.cast import TypeConvertor, convert
from datetime import datetime, date, timedelta
from dateutil import parser as date_parser


T = TypeVar("T", bound=type)


class Convertor(Mapping):
    """
    Used to convert data to certain datatypes.
    Conversion mappings need to be registered using the `register` method
    """

    def __init__(self):
        self.mappings: dict[type, TypeConvertor] = {}

    def register(self, dtype: T, converter: TypeConvertor[T]):
        """Registers a convertor for a data type

        Parameters
        ----------
        dtype
            Data type for which to use convertor
        converter
            Callable capable of converting data to dtype
        """

        self.mappings[dtype] = converter

    def convert(self, data, dtype: T) -> T:
        """Converts the data to the dtype. It will try to a registered convertor.
        If there wasn't registered any converter it will fallback to a default conversion.
        """
        if dtype in self.mappings:
            return self.mappings[dtype](data)

        return convert(data, dtype)

    def __getitem__(self, key):
        return self.mappings[key]

    def get(self, key):
        if key in self:
            return self[key]
        # Fallback
        return key

    def __contains__(self, key):
        return key in self.mappings

    def __len__(self):
        return len(self.mappings)

    def __iter__(self):
        yield from self.mappings


def bool_converter(val) -> bool:
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
