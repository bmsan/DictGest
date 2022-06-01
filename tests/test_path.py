from dictgest import Path


def test_basic():
    p = Path("")
    data = {
        "a": 1,
        "b": 2,
        "c": {"d": 4},
        "e": [{"g": 120}, {"f": 30, "g": 100}, {"f": 20, "g": 14}, {"f": 30, "g": 200}],
    }
    res = p.extract(data)
    assert res == data

    p = Path("a")
    res = p.extract(data)
    assert res == 1

    p = Path("c")
    res = p.extract(data)
    assert res == {"d": 4}

    p = Path("c/d")
    res = p.extract(data)
    assert res == 4

    p = Path("e/*{f=30}/g")
    res = p.extract(data)
    print(res)
    assert res == [100, 200]

    p = Path("e/f")
    res = p.extract(data)
    print(res)
    assert res == [30, 20, 30]
