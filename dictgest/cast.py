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

from dictgest.routes import Chart

T = TypeVar("T")
M = TypeVar("M", bound=Mapping)

TypeConverterMap = Mapping[type[T], Callable[[Any], T]]
RouteMap = Mapping[type, Any]
TypeConvertor = Callable[[Any], T]


@runtime_checkable
class TypeCastable(Protocol):
    """Runtime checkable protocol for classes that need type conversion.
    Classes can be decorated as TypeCastable using @typecast decorator
    """

    @staticmethod
    def __typecast__(
        data: dict[str, Any],
        mapping: Optional[TypeConverterMap],
        routes: Optional[Chart],
    ):
        ...


def convert_mapping(
    data: Mapping,
    dtype: type[T],
    mappings: TypeConverterMap[T] = None,
    routing: Chart = None,  # pylint: disable=W0613
) -> T:
    """Convert data to sepcified Mapping Annotated type

    Parameters
    ----------
    data
        Source data to be converted
    dtype
        Desired Mapping type of the result
    mappings, optional
        Converters for mapping types, by default None

    Returns
    -------
        data converted to dtype

    Raises
    ------
    ValueError
        _description_
    """
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
    except (TypeError, ValueError):
        res = copy.copy(data) if isinstance(data, origin) else {}
    key_type, val_type = args
    for key, val in data.items():
        key = convert(key, key_type, mappings)
        val = convert(val, val_type, mappings)
        res[key] = val
    return cast(T, res)


def convert_iterable(
    data,
    dtype: type[T],
    mappings: TypeConverterMap[T] = None,
    routing: Chart = None,  # pylint: disable=W0613
) -> T:
    """Convert data according to the annotated Iterable datatype

    Parameters
    ----------
    data
        Source data to be converted
    dtype
        Desired result iterable data type
    mappings, optional
        Predefined conversions, by default None

    Returns
    -------
       Converted data
    """
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


def convert_base_type(
    data: Any,
    dtype: type[T],
    type_mappings: TypeConverterMap[T] = None,
    routing: Chart = None,
) -> T:
    """
    Datatype conversion function when dtype isn't a generic alias
    See `convert` for details
    """
    if type_mappings and dtype in type_mappings:
        return type_mappings[dtype](data)

    # base type
    if issubclass(dtype, TypeCastable):
        # Type has been decorated with the @typecast decorator
        return dtype.__typecast__(data, type_mappings, routing)
    if routing and dtype in routing:
        if routing.typecast:
            return routing.typecast(dtype, data, type_mappings, routing)
        raise ValueError("routing.typecast was not set")
    # try default conversion
    return dtype(data)  # type: ignore


def convert_generic_alias(
    data: Any,
    dtype: type[T],
    type_mappings: TypeConverterMap[T] = None,
    routing: Chart = None,
) -> T:
    """
    Datatype conversion function for dtype of `types.GenericAlias`.
    See `convert` for details
    """
    if type_mappings and dtype in type_mappings:
        return type_mappings[dtype](data)

    origin = get_origin(dtype)
    assert isinstance(origin, type)
    if issubclass(origin, Mapping):
        if not isinstance(data, Mapping):
            raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
        return convert_mapping(data, dtype, type_mappings, routing)
    if not issubclass(origin, Iterable):
        raise ValueError(f"{origin}")
    if not isinstance(data, Iterable):
        raise TypeError(f"Cannot convert from {type(data)} to : {dtype}")
    return convert_iterable(data, dtype, type_mappings, routing)


def convert(
    data: Any,
    dtype: Optional[type[T]],
    type_mappings: TypeConverterMap[T] = None,
    routing: Chart = None,
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
    empty = inspect.Parameter.empty
    if dtype is None or dtype is empty:
        return data  # no datatype was specified
    if type(dtype) == type:  # pylint: disable=C0123
        if isinstance(data, dtype):
            return data  # already the right type
        return convert_base_type(data, dtype, type_mappings, routing)
    if type(dtype) == types.GenericAlias:  # pylint: disable=C0123
        return convert_generic_alias(data, dtype, type_mappings, routing)
    raise ValueError(f"{type(dtype)}, {dtype}")
