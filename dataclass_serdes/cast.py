import copy
import inspect
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
    types,
)

T = TypeVar("T", bound=type)

TypeConstructorMap = dict[type[T], Callable[[Any], T]]


@runtime_checkable
class TypeCastable(Protocol):
    @staticmethod
    def __typecast__(data: dict[str, Any], mapping: Optional[TypeConstructorMap]):
        ...


class Convertor:
    def __init__(self):
        self.mappings = {}

    def register(self, dtype: type, converter: Callable):
        self.mappings[dtype] = converter

    def convert(self, data, dtype: type):
        if dtype in self.mappings:
            return self.mappings[dtype](data)

        return convert(data, dtype)


def convert_mapping(data, dtype, mappings):
    origin = dtype.__origin__
    if not issubclass(origin, Mapping):
        raise ValueError()

    args = dtype.__args__
    assert len(args) == 2
    assert isinstance(data, Mapping)
    # Here we should actually try to create the mapping type
    # 1. Try to create the Mapping datatype
    # 2. If above fails try to copy if the original data is the desired datatype
    # 3. Fallback to dictionary
    try:
        res = origin()
    except Exception:
        if isinstance(data, origin):
            res = copy.copy(data)
        else:
            # TODO: Raise warning
            # TODO: Maybe look at default value
            res = {}
    key_type, val_type = args
    for key, val in data.items():
        key = convert(key, key_type, mappings)
        val = convert(val, val_type, mappings)
        res[key] = val
    return res


def convert_iterable(data, dtype, mappings):
    origin = dtype.__origin__
    if not issubclass(origin, Iterable):
        raise ValueError()

    args = dtype.__args__

    elements = []
    if len(args) == 1:
        for el in data:
            elements.append(convert(el, args[0], mappings))
    else:
        assert len(args) == len(data)
        for dt_val, el in zip(args, data):
            elements.append(convert(el, dt_val, mappings))

    res = origin(elements)

    return res


def convert(
    data: Any, dtype: Optional[type[T]], mappings: TypeConstructorMap = None
) -> T:
    if dtype in [None, inspect._empty]:
        return data
    if type(dtype) == type and isinstance(data, dtype):
        return data
    if mappings and dtype in mappings:
        return mappings[dtype](data)
    if type(dtype) == type:  # base type
        if issubclass(dtype, TypeCastable):
            return dtype.__typecast__(data, mappings)
        return dtype(data)
    elif type(dtype) == types.GenericAlias:
        origin = dtype.__origin__
        if issubclass(origin, Mapping):
            if not isinstance(data, Mapping):
                raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
            return convert_mapping(data, dtype, mappings)
        if issubclass(origin, Iterable):
            if not isinstance(data, Iterable):
                raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
            return convert_iterable(data, dtype, mappings)
        else:
            raise ValueError(f"{origin}")
    else:
        raise ValueError(f"{type(dtype)}, {dtype}")
