from typing import Annotated
import pytest
from dictgest.cast import convert


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


# if __name__ == '__main__':
