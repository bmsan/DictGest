from typing import Annotated
import pytest
from dataclasses import dataclass
from dataclass_serdes import from_dict
from dataclass_serdes.serdes import Path

def test_conversion():
    class A:
        def __init__(self, a, b: int, c: list[tuple[int, dict]], d: Annotated[list[str], Path('/a/b/c')]=1, e=2, f=3) -> None:
            self.a = a
            self.b = b
            self.c = c 
            self.d = d 
            self.e = e
            self.f = f
            
    data = {"a" : 10, "b": 20, "c": 30, "d": 40, "e": 50, "extra_field": 100 } 
    
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
            
    data = {"a" : 10, "b": 20, "c": 30, "d": 40,  "extra_field": 100 } 
    
    result = from_dict(A, data)
    for key, val in result.__dict__.items():
        if key in data:
            assert val == data[key]