def flatten(data: list) -> list:
    """Flatten a nested list
    Eg: [[a, b, c], [d, e]] => [a, b, c, d, e]

    """
    if data and isinstance(data[0], (list, tuple)):
        out = []
        for elem in data:
            out += elem
        return out
    return data
