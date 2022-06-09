import inspect
from typing import (  # type: ignore
    Any,
    Callable,
    Iterable,
    Mapping,
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
    convert_types, optional
        if target fields should be converted to typing hint types.

    Returns
    -------
        The converted datatype

    """
    empty = inspect.Parameter.empty
    params = inspect.signature(target).parameters

    if routing:
        if isinstance(routing, Route):
            routing = Chart({target: routing})
        elif not isinstance(routing, Chart):
            routing = Chart(routing)
        routing.typecast = from_dict
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
