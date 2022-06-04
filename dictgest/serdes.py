# from datetime import datetime
import inspect
from typing import Any, Callable, Optional, TypeVar, types, _AnnotatedAlias, Union

# from dateutil import parser as date_parser
from .cast import TypeConverterMap, convert, TypeCastable
from functools import partial
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


def from_dict(
    target: type[T],
    data: dict,
    type_mappings: TypeConverterMap = default_convertor,
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
    params = inspect.signature(target).parameters
    kwargs = {}
    for name, prop in params.items():
        anot = prop.annotation

        dtype: Optional[type] = None
        if type(anot) in [type, types.GenericAlias]:
            dtype = anot
        elif type(anot) == _AnnotatedAlias:
            dtype = anot.__origin__

        _path = None
        if hasattr(prop.annotation, "__metadata__"):
            for meta in prop.annotation.__metadata__:
                if isinstance(meta, Path):
                    _path = meta
                    break

        if _path:
            val = _path.get(data, prop.default)
        else:
            val = data.get(name, prop.default)
        if val == inspect._empty:
            raise ValueError(f"Missing parameter {name}")
        if convert_types:
            val = convert(val, dtype, type_mappings)
        kwargs[name] = val

    return target(**kwargs)


def flatten(data: list):
    if len(data) > 0 and isinstance(data[0], (list, tuple)):
        out = []
        for elem in data:
            out += elem
        return out
    return data


class Path:
    """Data type annotation for class attributes that can signal:
      - renaming: maping a dictionary field to an attribute with a different name
      - rerouting: mapping a nested dictionary field to a class attribute
      - Setting a default data converter for the field

    Its is used in conjunction with Pythons ``Typing.Annotated`` functionality

    .. code-block:: python

        class Model:
            def __init__(self,
                        // the module will extract the 'field1' key
                        field1,
                        // the module will extract the 'name' key
                        field2 : Annotated[str, Path('name')]
                        // the module will extract the ['p1']['p2']['val'] field
                        field3 : Annotated[str, Path('p1/p2/val')]
                        )

    """

    def __init__(self, path: str, extractor: Callable = None, flatten_en=True) -> None:
        """

        Parameters
        ----------
        path
            Extraction path(key/keys) from dictionary.
            Eg: path='name1' will map the annotated field to a dictionary key 'name1'
            Eg: path='p1/p2/name2' will map the annotated field to nested_data['p1']['p2']['name2']
        extractor, optional
            Callable to extract/convert the data from the specified path, by default None
        flatten_en, optional
            In case the path contains an element which is a list, flatten it's elements

            Eg: data = {'a': [
                              [{'b': 1}, {'b': 2}],
                              [{'b': 3}]
                            ]}
            path='a/b' with flatten_en would result in the extraction of [1, 2, 3]
        """

        self.path = path
        self.parts = path.split("/")
        self.extractor = extractor
        self.flatten_en = flatten_en

    def extract(self, data: dict[str, Any]):
        for part in self.parts:

            if part.startswith("*"):
                if not isinstance(data, (list, tuple)):
                    raise TypeError()
                if "{" in part:
                    name, val = part.split("{", 1)[1].split("}", 1)[0].split("=")
                    data = [el for el in data if name in el and str(el[name]) == val]
            else:
                if isinstance(data, (list, tuple)):
                    data = [o[part] for o in data if part in o]
                    if self.flatten_en:
                        data = flatten(data)

                else:
                    if part == "":
                        pass
                    else:
                        if isinstance(data, int):
                            print()
                        data = data[part]
        if self.extractor is not None:
            data = self.extractor(data)
        return data

    def get(self, data: dict, default):
        try:
            return self.extract(data)
        except KeyError:
            return default
