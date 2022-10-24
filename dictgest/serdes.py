import inspect
from typing import (  # type: ignore
    Iterable,
    Optional,
    TypeVar,
    Union,
    types,
    _AnnotatedAlias,
)  # type: ignore
from functools import partial

from dictgest.routes import Chart, Path, Route

from .cast import TypeConverterMap, convert
from .converter import default_convertor

T = TypeVar("T", bound=type)


def typecast(cls):
    """
    Decorates a python class(including dataclass)
    to enable automatic type conversion.
    Can be used as a class decorator

    Examples
    --------
    It can be used as a class decorator

    >>> @typecast
    >>> class MyClass:
    >>> ...

    But also as a function call

    >>> typecast(MyClass)

    Returns
    -------
        The decorated class
    """
    cls.__typecast__ = partial(from_dict, cls)
    return cls


def _get_dtype_from_anot(anot) -> Optional[type]:
    dtype: Optional[type] = None
    if type(anot) in [type, types.GenericAlias]:
        dtype = anot
    elif type(anot) == _AnnotatedAlias:
        dtype = anot.__origin__
    return dtype


def _get_path_from_anot(anot):
    _path = None
    if hasattr(anot, "__metadata__"):
        for meta in anot.__metadata__:
            if isinstance(meta, Path):
                _path = meta
                break
    return _path


def _get_route_path(anot, name: str, route_template: Optional[Route]):
    anot_path = _get_path_from_anot(anot)
    template_path = route_template[name] if route_template else None

    if anot_path and template_path:
        raise ValueError(
            f"For field {name}, the path was found in both the template and destination path"
        )

    return template_path or anot_path


def _construct_routing(
    dtype: type, routing: Union[Route, dict[type, Route], Chart, None]
) -> Optional[Chart]:
    chart = None
    if routing:
        if isinstance(routing, Chart):
            chart = routing
        elif isinstance(routing, Route):
            chart = Chart({dtype: routing})
        else:
            chart = Chart(routing)
        chart.typecast = from_dict
    return chart


def from_dict(
    target: type[T],
    data: dict,
    type_mappings: TypeConverterMap = default_convertor,
    routing: Union[Route, dict[type, Route], Chart] = None,
    convert_types: bool = True,
) -> T:
    """Converts a dictionary to the desired target type.

    Parameters
    ----------
    target
        Target conversion type
    data
        dictionary data to be converted to target type
    type_mappings, optional
        custom conversion mapping for datatypess, by default None
    routing, optional
        custom conversion routing for fieldnames, see `Route`
    convert_types, optional
        if target fields should be converted to typing hint types.

    Returns
    -------
        The converted datatype

    """
    empty = inspect.Parameter.empty
    params = inspect.signature(target).parameters

    routing = _construct_routing(target, routing)
    router = routing[target] if routing and target in routing else None

    kwargs = {}
    for name, prop in params.items():
        anot = prop.annotation

        dtype = _get_dtype_from_anot(anot)
        _path = _get_route_path(anot, name, router)
        val = _path.get(data, prop.default) if _path else data.get(name, prop.default)
        if val == empty:
            raise ValueError(f"Missing parameter {name}")
        if convert_types:
            val = convert(val, dtype, type_mappings, routing)
        kwargs[name] = val

    return target(**kwargs)  # type: ignore


def _get_row(data: list[list], transpose: bool):
    if transpose:
        for idx in range(len(data[0])):
            yield [row[idx] for row in data]
    else:
        yield from data


def table_to_item(
    target: type[T],
    data: list[list],
    header: list[str],
    transpose: bool = False,
    type_mappings: TypeConverterMap = default_convertor,
    routing: Union[Route, dict[type, Route], Chart] = None,
    convert_types: bool = True,
    # pylint: disable=R0913
) -> T:
    """Converts a table (2d structure) to the desired target type.
        The table columns are regarded as target fields and the
        field names are given in the header parameter.
    Parameters
    ----------
    target
        Target conversion type
    data
        2d table (nested lists) that will be converted
    header
        column names of the 2d table
    transpose
        switch rows with columns(eg: first row becomes first column and viceversa)
    type_mappings, optional
        custom conversion mapping for datatypess, by default None
    routing, optional
        custom conversion routing for fieldnames, see `Route`
    convert_types, optional
        if target fields should be converted to typing hint types.

    Returns
    -------
        The converted datatype

    """

    if transpose:
        if len(data) != len(header):
            raise ValueError(
                f"Header has {len(header)} elements while table {len(data)}"
            )
        dict_of_lists = {key: item for item, key in zip(data, header)}
    else:
        if len(data[0]) != len(header):
            raise ValueError(
                f"Header has {len(header)} elements while table {len(data[0])}"
            )
        dict_of_lists = {
            key: [row[col_idx] for row in data] for col_idx, key in enumerate(header)
        }

    return from_dict(
        target,
        dict_of_lists,
        type_mappings=type_mappings,
        routing=routing,
        convert_types=convert_types,
    )


def table_to_items(
    target: type[T],
    data: list[list],
    header: list[str],
    transpose: bool = False,
    type_mappings: TypeConverterMap = default_convertor,
    routing: Union[Route, dict[type, Route], Chart] = None,
    convert_types: bool = True,
    # pylint: disable=R0913
) -> Iterable[T]:
    """Converts a table (2d structure) to a list of items of the desired target type.
        Each table row is regarded as an item to be converted.
        The field names are given in the header parameter.

    Parameters
    ----------
    target
        Target conversion type
    data
        2d table (nested lists) that will be converted
    header
        column names of the 2d table
    transpose
        switch rows with columns(eg: first row becomes first column and viceversa)
    type_mappings, optional
        custom conversion mapping for datatypess, by default None
    routing, optional
        custom conversion routing for fieldnames, see `Route`
    convert_types, optional
        if target fields should be converted to typing hint types.

    Returns
    -------
        The converted datatype

    """
    for row_idx, row in enumerate(_get_row(data, transpose)):
        if len(row) != len(header):
            raise ValueError(
                f"Header has {len(header)} elements while table row[{row_idx}] has {len(data)}"
            )
        dict_to_convert = {key: item for item, key in zip(row, header)}

        yield from_dict(
            target,
            dict_to_convert,
            type_mappings=type_mappings,
            routing=routing,
            convert_types=convert_types,
        )
