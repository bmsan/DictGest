import copy
import inspect
from typing import (  # type: ignore
    Any,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    TypeVar,
    cast,
    get_args,
    get_origin,
    runtime_checkable,
    types,
)

T = TypeVar("T")
M = TypeVar("M", bound=Mapping)

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


def convert_mapping(
    data: Mapping,
    dtype: type[M],
    mappings: TypeConverterMap[M] = None,
) -> M:
    origin = get_origin(dtype)
    args = get_args(dtype)
    assert isinstance(origin, type)

    if not issubclass(origin, MutableMapping):
        raise ValueError()

    assert len(args) == 2
    assert isinstance(data, Mapping)
    # Here we should actually try to create the mapping type
    # 1. Try to create the Mapping datatype
    # 2. If above fails try to copy if the original data is the desired datatype
    # 3. Fallback to dictionary
    # res: Mapping = {}
    try:
        res = origin()
    except Exception:
        res = copy.copy(data) if isinstance(data, origin) else {}
    key_type, val_type = args
    for key, val in data.items():
        key = convert(key, key_type, mappings)
        val = convert(val, val_type, mappings)
        res[key] = val
    return cast(M, res)


def convert_iterable(data, dtype: type[T], mappings: TypeConverterMap[T] = None) -> T:
    origin = get_origin(dtype)
    args = get_args(dtype)
    assert isinstance(origin, type)
    if not issubclass(origin, Iterable):
        raise ValueError()

    elements: list[Any] = []
    if len(args) == 1:
        elements.extend(convert(el, args[0], mappings) for el in data)
    else:
        assert len(args) == len(data)
        elements.extend(convert(el, dt_val, mappings) for dt_val, el in zip(args, data))

    return origin(elements)  # type: ignore


def convert(
    data: Any, dtype: Optional[type[T]], type_mappings: TypeConverterMap[T] = None
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
    if dtype is None or dtype is inspect._empty:
        return data  # no datatype was specified
    if type(dtype) == type and isinstance(data, dtype):
        return data  # already the right type
    if type_mappings and dtype in type_mappings:
        return type_mappings[dtype](data)
    if type(dtype) == type:  # base type
        if issubclass(dtype, TypeCastable):
            # Type has been decorated with the @typecast decorator
            return dtype.__typecast__(data, type_mappings)
        # try default conversion
        return dtype(data)  # type: ignore
    elif type(dtype) == types.GenericAlias:
        origin = get_origin(dtype)
        assert isinstance(origin, type)
        if issubclass(origin, Mapping):
            if not isinstance(data, Mapping):
                raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
            return convert_mapping(data, dtype, type_mappings)
        if not issubclass(origin, Iterable):
            raise ValueError(f"{origin}")
        if not isinstance(data, Iterable):
            raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
        return convert_iterable(data, dtype, type_mappings)
    else:
        raise ValueError(f"{type(dtype)}, {dtype}")
