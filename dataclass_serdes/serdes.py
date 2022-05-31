# from datetime import datetime
import inspect
from typing import Any, Callable, Optional, TypeVar, types, _AnnotatedAlias

# from dateutil import parser as date_parser
from .cast import convert
from functools import partial


def typecast(cls):
    cls.__typecast__ = partial(from_dict, cls)
    return cls


T = TypeVar("T", bound=type)


def from_dict(target: type[T], data: dict, mappings=None, convert_types=True) -> T:
    """Construct an object based on it's type
    and on a keyword argument dictionary
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
        # types.GenericAlias
        # anot = prop.annotation
        # __origin__
        # __args__

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
            val = convert(val, dtype, mappings)
        kwargs[name] = val

    return target(**kwargs)


def set_common_fields(target: T, data: dict):
    """Construct an object based on it's type
    and on a keyword argument dictionary
    """
    params = inspect.signature(target.__class__).parameters
    for name in params:
        if name in data:
            setattr(target, name, data[name])


S = TypeVar("S")


def transfer_dc_fields(src: T, dst: S, allow_partial=False):
    """Construct an object based on it's type
    and on a keyword argument dictionary
    """
    src_params = inspect.signature(src.__class__).parameters
    dst_params = inspect.signature(dst.__class__).parameters
    for name in dst_params:
        if name not in src_params:
            if not allow_partial:
                raise TypeError(f"Missing field {name} in {src}")
        setattr(src, name, getattr(dst, name))


def flatten(data: list):
    if len(data) > 0 and isinstance(data[0], (list, tuple)):
        out = []
        for elem in data:
            out += elem
        return out
    return data


class Path:
    def __init__(self, path: str, extractor: Callable = None, flatten_en=True) -> None:
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
