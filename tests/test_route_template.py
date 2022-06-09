from dataclasses import dataclass
from typing import Annotated
import pytest
from dictgest.cast import convert
from dictgest import Path, typecast, from_dict, default_convertor
from dictgest.routes import Chart
from dictgest.serdes import Route
from .utils import check_fields
from datetime import datetime


def test_route_template():
    data = {
        "a": 3.4,
        "b": 4,
        "c": {
            "d": 10.1,
            "de": {"e": 10.2, "f": [{"g": 10.3}, {"g": 11}, {"g": 12.1}, {"g": 13.2}]},
        },
    }

    @dataclass
    class A1:
        a: int
        b: float
        d: Annotated[int, "some other annotation"]
        e: int
        f: list[int]

    A1_route = Route(d="c/d", e=Path("c/de/e"), f="c/de/f/g")

    a = from_dict(A1, data, convert_types=False, routing=A1_route)
    check_fields(
        a, {"a": 3.4, "b": 4, "d": 10.1, "e": 10.2, "f": [10.3, 11, 12.1, 13.2]}
    )

    a = from_dict(A1, data, routing=A1_route)
    check_fields(a, {"a": 3, "b": 4.0, "d": 10, "e": 10, "f": [10, 11, 12, 13]})


def test_chart_template():
    data = {
        "a": 3.4,
        "b": 4,
        "c": {
            "d": 10.1,
            "de": {"e": 10.2, "f": [{"g": 10.3}, {"g": 11}, {"g": 12.1}, {"g": 13.2}]},
        },
    }

    @dataclass
    class B1:
        x: float
        y: list[float]

    @dataclass
    class A1:
        a: int
        b: float
        d: Annotated[int, "some other annotation"]
        e: B1
        f: list[int]

    @dataclass
    class C1:
        a: int
        b: float
        d: Annotated[int, "some other annotation"]
        f: list[int]

    routes = {
        A1: Route(d="c/d", e=Path("c/de"), f="c/de/f/g"),
        B1: Route(x="e", y=Path("f/g")),
    }

    # a = from_dict(A1, data, convert_types=False, routing=routes)
    # check_fields(
    #     a, {"a": 3.4, "b": 4, "d": 10.1, "e": 10.2, "f": [10.3, 11, 12.1, 13.2]}
    # )

    a = from_dict(A1, data, routing=routes)
    check_fields(a, {"a": 3, "b": 4.0, "d": 10, "f": [10, 11, 12, 13]})
    check_fields(a.e, {"x": 10.2, "y": [10.3, 11, 12.1, 13.2]})

    a = from_dict(A1, data, routing=Chart(routes))
    check_fields(a, {"a": 3, "b": 4.0, "d": 10, "f": [10, 11, 12, 13]})
    check_fields(a.e, {"x": 10.2, "y": [10.3, 11, 12.1, 13.2]})

    route = Route(d="c/d", f="c/de/f/g")

    c = from_dict(C1, data, routing=route)
    check_fields(c, {"a": 3, "b": 4.0, "d": 10, "f": [10, 11, 12, 13]})

    c = from_dict(C1, data, routing={C1: route})
    check_fields(c, {"a": 3, "b": 4.0, "d": 10, "f": [10, 11, 12, 13]})

    c = from_dict(C1, data, routing=Chart({C1: route}))
    check_fields(c, {"a": 3, "b": 4.0, "d": 10, "f": [10, 11, 12, 13]})

    c = from_dict(C1, data, convert_types=False, routing=route)
    check_fields(c, {"a": 3.4, "b": 4.0, "d": 10.1, "f": [10.3, 11, 12.1, 13.2]})
