from dataclasses import dataclass
from typing import Annotated
import pytest
from dictgest.cast import convert
from dictgest import Path, typecast, from_dict, default_convertor
from .utils import check_fields
from datetime import datetime


def test_float():
    r = convert(3.4, float)
    assert r == 3.4
    assert isinstance(r, float)

    r = convert("3.4", float)

    assert r == 3.4
    assert isinstance(r, float)


def test_int():
    r = convert(3.4, int)
    assert r == 3
    assert isinstance(r, int)


def test_iterators():
    r = convert([3.4, "7", "8"], list[int])
    assert r == [3, 7, 8]

    r = convert([3.4, "7", "8"], tuple[float, str, int])
    assert r == (3.4, "7", 8)

    r = convert([3.4, "7", "8"], set[str])
    assert r == set(["3.4", "7", "8"])


def test_nested_iterators():
    r = convert(
        [
            (1, 2, 3, "4"),
            ("3.4", "5", 7.6, 9.2),
            (("a", "bc", "de"), ["a", "a", "b", "a"]),
        ],
        tuple[list[int], set[float], list[set[str]]],
    )


def test_dict():
    r = convert({"aa": "3.4", 4: 6.5, "bb": "1"}, dict[str, float])
    assert r == {"aa": 3.4, "4": 6.5, "bb": 1}

    r = convert({"aa": ["3.4"], 4: [6.5], "bb": ["1"]}, dict[str, tuple])
    assert r == {"aa": ("3.4",), "4": (6.5,), "bb": ("1",)}

    r = convert({"aa": ["3.4"], 4: [6.5], "bb": ["1"]}, dict[str, tuple[float]])
    assert r == {"aa": (3.4,), "4": (6.5,), "bb": (1,)}

    r = convert({"aa": ["3.4"], 4: [6.5], "bb": ["1"]}, dict)
    print(r, type(r))

    r = convert({"aa": ["3.4"], 4: [6.5], "bb": ["1"]}, dict)
    assert r == {"aa": ["3.4"], 4: [6.5], "bb": ["1"]}


def test_mappings():
    data = {
        "a": 3.4,
        "b": 4,
        "c": {
            "d": 10.1,
            "de": {"e": 10.2, "f": [{"g": 10.3}, {"g": 11}, {"g": 12.1}, {"g": 13.2}]},
        },
    }

    @dataclass
    class A:
        a: int
        b: float
        d: Annotated[int, Path("c/d")]
        e: Annotated[int, Path("c/de/e")]
        f: Annotated[list[int], Path("c/de/f/g")]

    a = from_dict(A, data, convert_types=False)
    check_fields(
        a, {"a": 3.4, "b": 4, "d": 10.1, "e": 10.2, "f": [10.3, 11, 12.1, 13.2]}
    )

    a = from_dict(A, data)
    check_fields(a, {"a": 3, "b": 4.0, "d": 10, "e": 10, "f": [10, 11, 12, 13]})

    a = from_dict(A, data, None)
    check_fields(a, {"a": 3, "b": 4.0, "d": 10, "e": 10, "f": [10, 11, 12, 13]})

    type_mapping = {float: lambda x: f"f{x}", int: lambda x: f"i{x}"}
    a = from_dict(A, data, type_mapping)

    # we only convert elements of different types
    check_fields(
        a,
        {
            "a": "i3.4",
            "b": "f4",
            "d": "i10.1",
            "e": "i10.2",
            "f": ["i10.3", 11, "i12.1", "i13.2"],
        },
    )


def test_default_converter():
    data = {
        "x": "lol",
        "a": "yes",
        "b": "false",
        "c": 0,
        "d": "2020-01-01",
        "e": 1640988000,
    }

    bool_convertor = default_convertor.get_converter(bool)

    def custom_bool_convertor(val):
        if val == "lol":
            return True
        return bool_convertor(val)

    default_convertor.register(bool, custom_bool_convertor)

    @dataclass
    class A:
        x: bool
        a: bool
        b: bool
        c: bool
        d: datetime
        e: datetime

    a = from_dict(A, data)
    check_fields(
        a,
        {
            "x": True,
            "a": True,
            "b": False,
            "c": False,
            "d": datetime(2020, 1, 1, 0, 0),
            "e": datetime(2021, 12, 31, 22, 0),
        },
    )


def test_negative():
    with pytest.raises(Exception):
        convert(list[{"a": 1, "b": 2}, [1, 2]], list[dict])

    with pytest.raises(Exception):
        convert([3.14, "str"], dict[str, list])


def test_flatten():
    data = {
        "a": 3.4,
        "b": 4,
        "c": {
            "de": {
                "e": 10.2,
                "f": [
                    {"g": [10.3, 100]},
                    {"g": [11, 200]},
                    {"g": [12.1, 300]},
                    {"g": [13.2, 400]},
                ],
            },
        },
    }

    @dataclass
    class A:
        a: int
        b: float
        f: Annotated[list[int], Path("c/de/f/g")]
        g: Annotated[list[int], Path("c/de/f/g", flatten_en=False)]

    a = from_dict(A, data, convert_types=False)
    check_fields(
        a,
        {
            "a": 3.4,
            "b": 4,
            "d": 10.1,
            "e": 10.2,
            "f": [10.3, 100, 11, 200, 12.1, 300, 13.2, 400],
            "g": [[10.3, 100], [11, 200], [12.1, 300], [13.2, 400]],
        },
    )
