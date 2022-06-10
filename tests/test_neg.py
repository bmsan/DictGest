from typing import Annotated, Any, Protocol, runtime_checkable
import pytest
from dataclasses import dataclass
from dictgest import from_dict, typecast
from dictgest import Path
from dictgest.routes import Chart, Route


def check_fields(obj, ref_dict):
    for key, val in obj.__dict__.items():
        if key in ref_dict:
            assert val == ref_dict[key]


def test_missing_dict_field():
    @dataclass
    class A1:
        a: int
        b: float
        c: str
        d: int

    data = {"a": 10, "b": 20, "d": 40}

    with pytest.raises(Exception):
        result = from_dict(A1, data)


def test_type_error():
    @dataclass
    class A1:
        a: int
        b: float
        d: int

    data = {"a": 10, "b": {"f": 20}, "d": 40}

    with pytest.raises(TypeError):
        from_dict(A1, data)


def test_route_error():
    @dataclass
    class A1:
        a: int
        b: float
        d: int

    data = {"a": 10, "b": 20, "de": 40}

    with pytest.raises(ValueError):
        from_dict(A1, data, routing=Route(f="d"))


def test_multiple_path_error():
    @dataclass
    class A1:
        a: int
        b: float
        d: Annotated[int, Path("de")]

    data = {"a": 10, "b": 20, "de": 40}

    with pytest.raises(ValueError):
        from_dict(A1, data, routing=Route(d="d"))


def test_init():
    with pytest.raises(TypeError):
        Chart()

    with pytest.raises(TypeError):
        Chart(Route(x="a"))

    with pytest.raises(TypeError):
        Route(x={})

    with pytest.raises(TypeError):
        Route(x=None)

    with pytest.raises(ValueError):
        Route()

    @dataclass
    class A1:
        a: int

    with pytest.raises(ValueError):
        Chart({A1: Route(b="")})


def test_path_wildcard():
    @dataclass
    class A1:
        a: Annotated[list[str], Path("*{a==3}")]

    with pytest.raises(TypeError):
        from_dict(A1, {"a": 3.14})
