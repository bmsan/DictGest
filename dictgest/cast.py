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

TypeConverterMap = Mapping[type[T], Callable[[Any], T]]
TypeConvertor = Callable[[Any], T]


@runtime_checkable
class TypeCastable(Protocol):
    """Runtime checkable protocol for classes that need type conversion.
    Classes can be decorated as TypeCastable using @typecast decorator
    """

    @staticmethod
    def __typecast__(data: dict[str, Any], mapping: Optional[TypeConverterMap]):
        ...


def convert_mapping(data, dtype, mappings: TypeConverterMap):
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


def convert_iterable(data, dtype: types.GenericAlias, mappings: TypeConverterMap):
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
    data: Any, dtype: Optional[type[T]], type_mappings: TypeConverterMap = None
) -> T:
    """Converts a data value to a specified data type.

    Parameters
    ----------
    data
        Data to be converted
    dtype
        Type to convert
    type_mappings, optional
        predefined convertor map for certain data types

    Returns
    -------
        The converted datatype
    """
    if dtype in [None, inspect._empty]:
        return data  # no datatype was specified
    if type(dtype) == type and isinstance(data, dtype):
        return data  # already the right type
    if type_mappings and dtype in type_mappings:
        return type_mappings[dtype](data)
    if type(dtype) == type:  # base type
        if issubclass(dtype, TypeCastable):
            # Type has been decorated with the @typecast decorator
            return dtype.__typecast__(data, type_mappings)
        return dtype(data)  # try default conversion
    elif type(dtype) == types.GenericAlias:
        origin = dtype.__origin__
        if issubclass(origin, Mapping):
            if not isinstance(data, Mapping):
                raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
            return convert_mapping(data, dtype, type_mappings)
        if issubclass(origin, Iterable):
            if not isinstance(data, Iterable):
                raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
            return convert_iterable(data, dtype, type_mappings)
        else:
            raise ValueError(f"{origin}")
    else:
        raise ValueError(f"{type(dtype)}, {dtype}")
