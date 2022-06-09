from typing import Annotated, Any, Protocol, runtime_checkable
import pytest
from dataclasses import dataclass
from dictgest import from_dict, typecast
from dictgest import Path


def check_fields(obj, ref_dict):
    for key, val in obj.__dict__.items():
        if key in ref_dict:
            assert val == ref_dict[key]


def test_conversion():
    @typecast
    class A:
        # def __init__(self, a: Any, b: int, c: list[tuple[int, dict]], d: Annotated[list[str], Path('/a/b/c')]=1, e=2, f=3) -> None:
        def __init__(self, a: Any, b: int, c, d: float, e=2, f=3) -> None:
            self.a = a
            self.b = b
            self.c = c
            self.d = d
            self.e = e
            self.f = f

    data = {"a": 10, "b": 20, "c": 30, "d": 40, "e": 50, "extra_field": 100}

    result = from_dict(A, data)
    for key, val in result.__dict__.items():
        if key in data:
            assert val == data[key]


def test_conversion_dataclass():
    @dataclass
    class A:
        a: int
        b: int
        c: int
        d: int = 4
        e: int = 5

    data = {"a": 10, "b": 20, "c": 30, "d": 40, "extra_field": 100}

    result = from_dict(A, data)
    check_fields(result, data)


def test_type_conversion():
    @typecast
    class A:
        # def __init__(self, a: Any, b: int, c: list[tuple[int, dict]], d: Annotated[list[str], Path('/a/b/c')]=1, e=2, f=3) -> None:
        def __init__(self, a: Any, b: int, c: str, d: float, e=2, f=3) -> None:
            self.a = a
            self.b = b
            self.c = c
            self.d = d
            self.e = e
            self.f = f

    data = {"a": 10, "b": 20.5, "c": 30, "d": 40, "e": 50, "extra_field": 100}
    ref_data = {"a": 10, "b": 20, "c": "30", "d": 40, "e": 50, "f": 3}

    result = from_dict(A, data, convert_types=None)
    check_fields(result, data)

    result = from_dict(A, data)
    check_fields(result, ref_data)


def test_type_conversion_annotated():
    @typecast
    class A:
        # def __init__(self, a: Any, b: int, c: list[tuple[int, dict]], d: Annotated[list[str], Path('/a/b/c')]=1, e=2, f=3) -> None:
        def __init__(
            self,
            a: Any,
            b: int,
            c: Annotated[str, Path("ccc")],
            d: Annotated[float, Path("x/y/d")],
            e=2,
            f=3,
        ) -> None:
            self.a = a
            self.b = b
            self.c = c
            self.d = d
            self.e = e
            self.f = f

    data = {
        "a": 10,
        "b": 20.5,
        "ccc": 30,
        "x": {"y": {"d": 40}},
        "e": 50,
        "extra_field": 100,
    }
    ref_data = {"a": 10, "b": 20, "c": "30", "d": 40, "e": 50, "f": 3}

    result = from_dict(A, data)
    check_fields(result, ref_data)


def test_type_conversion_advanced():
    @typecast
    class C:
        # def __init__(self, a: Any, b: int, c: list[tuple[int, dict]], d: Annotated[list[str], Path('/a/b/c')]=1, e=2, f=3) -> None:
        def __init__(self, x: Any, y: int, z: str) -> None:
            self.x = x
            self.y = y
            self.z = z

    @typecast
    @dataclass
    class B:
        a: list[tuple[float, str]]
        b: Any
        c: dict[float, list[C]]
        d: int = 4
        e: int = 5

    @typecast
    class A:
        def __init__(self, a: Any, b: int, c: B, d: float, e=2, f=3) -> None:
            self.a = a
            self.b = b
            self.c = c
            self.d = d
            self.e = e
            self.f = f

    data = {
        "a": 10,
        "b": 20.5,
        "c": {
            "a": (["3.14", "el0"], [20, "el2"], ["31", "el2"]),
            "b": "second",
            "c": {
                10: [{"x": 1, "y": 2, "z": 3}, {"x": 10, "y": "20", "z": 30}],
                "20": ({"x": 11, "y": "12", "z": 13}, {"x": 110, "y": 120, "z": 130}),
            },
        },
        "d": 40,
        "e": 50,
        "extra_field": 100,
    }

    result = from_dict(A, data)
    print(result)


def test_type_conversion_advanced_annotated():
    @typecast
    class C:
        def __init__(self, x: Any, y: int, z: str) -> None:
            self.x = x
            self.y = y
            self.z = z

    @typecast
    @dataclass
    class B:
        a: list[tuple[float, str]]
        b: Any
        c: Annotated[dict[float, list[C]], Path("c1/c2/c3")]
        d: int = 4
        e: int = 5

    @typecast
    class A:
        def __init__(
            self, a: Any, b: int, c: Annotated[B, Path("ccc")], d: float, e=2, f=3
        ) -> None:
            self.a = a
            self.b = b
            self.c = c
            self.d = d
            self.e = e
            self.f = f

    data = {
        "a": 10,
        "b": 20.5,
        "ccc": {
            "a": (["3.14", "el0"], [20, "el2"], ["31", "el2"]),
            "b": "second",
            "c1": {
                "c2": {
                    "c3": {
                        10: [{"x": 1, "y": 2, "z": 3}, {"x": 10, "y": "20", "z": 30}],
                        "20": (
                            {"x": 11, "y": "12", "z": 13},
                            {"x": 110, "y": 120, "z": 130},
                        ),
                    }
                }
            },
        },
        "d": 40,
        "e": 50,
        "extra_field": 100,
    }

    result = from_dict(A, data)
    print(result)
