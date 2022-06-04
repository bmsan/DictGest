# DictGest - Python Dictionary Ingestion

[![Code Coverage](https://codecov.io/gh/bmsan/dictgest/branch/main/graph/badge.svg?token=WHTIAW8C85)](https://codecov.io/gh/bmsan/dictgest)
[![CI status](https://github.com/bmsan/dictgest/workflows/CI/badge.svg)](https://github.com/bmsan/dictgest/actions?queryworkflow%3ACI+event%3Apush+branch%3Amain)
[![Docs](https://readthedocs.org/projects/dictgest/badge/?version=latest)](https://readthedocs.org/projects/dictgest)
[![Discord](https://img.shields.io/discord/981859018836426752?label=Discord%20chat&style=flat)](https://discord.gg/yBb99rxBUZ)

# Description

When interacting with external REST APIs or with external configuration files we usually do not have control 
over the received data structure/format.

`DictGest` makes ingesting dictionary data into python objects(dataclasss objects included) easy when the dictionary data doesn't match 1 to 1 with the Python class:
  - The dictionary might have extra fields that are of no interest
  - The keys names in the dictionary do not match the class attribute names
  - The structure of nested dictionaries does not match the class structure
  - The data types in the dictionary do not match data types of the target class

# Examples

## Example 1: Trivial Example - Handling Extra parameters
The first most basic and trivial example is ingesting a dictionary that has extra data not of interest

```python
from dictgest import from_dict
```

![](https://github.com/bmsan/DictGest/blob/main/docs/source/ex1.png?raw=true)

```python
car = from_dict(Car, dict_data)
```

## Example 2: Data mapping renaming & rerouting

```python
from typing import Annotated
from dataclasses import dataclass
from dictgest import from_dict, Path
```


![](https://github.com/bmsan/DictGest/blob/main/docs/source/ex2.png?raw=true)

```python
article = from_dict(Article, news_api_data)
meta = from_dict(ArticleMeta, news_api_data)
stats = from_dict(ArticleStats, news_api_data)
```

The full working example can be found in the [examples folder](https://github.com/bmsan/DictGest/blob/main/examples/news_example.py)


## Example 3: Data type enforcing

Sometimes the data coming from external sources might have different datatypes than what we desire. `dictgen` can do type conversion for you.



```py
from dataclasses import dataclass
from dictgest import from_dict, typecast 

@typecast # Makes the class type convertable when encountered as typing hint
@dataclass # The dataclass is just an example, it could have an normal class
class Measurment:
    temp: float
    humidity: float


class Sensor:
    def __init__(
        self, name: str, location: str, uptime: float, readings: list[Measurment]
    ):
        ...
```

![](https://github.com/bmsan/DictGest/blob/main/docs/source/ex3.png?raw=true)

The conversions shown above were enabled by setting the `@typecast` decorator for the targetted classes.

The full working example can be found in the [examples folder](https://github.com/bmsan/DictGest/blob/main/examples/typeconvert_example.py)



## Example 4: Custom Data extraction/conversion for a specific field

```py
from typing import Annotated
from dictgest import Path, from_dict


def extract_votes(data):
    # creating a new value from two individual fields and converting them
    return int(data["positive"]) + int(data["negative"])


class Votes:
    def __init__(
        self,
        title,
        total_votes: Annotated[int, Path("details/votes", extractor=extract_votes)],
    ):
        ...

article_data = {
    "title": "Python 4.0 will...",
    "details": {"votes": {"positive": "245", "negative": "30"}},
}


votes = from_dict(Votes, article_data)

```

The full working example can be found in the [examples folder](https://github.com/bmsan/DictGest/blob/main/examples/extract_example.py)



## Example 5: Custom Data conversion for a specific type

```py
from dataclasses import dataclass
from dictgest import default_convertor, from_dict

# Get any already registered bool convertor
default_bool_conv = default_convertor.get(bool)

# create a custom converter
def custom_bool_conv(val):
    if val == "oups":
        return False

    # Let the other cases be treated as before
    return default_bool_conv(val)


# register the custom converter for bool
default_convertor.register(bool, custom_bool_conv)


@dataclass
class Result:
    finished: bool
    notified: bool


result = from_dict(Result, {"finished": True, "notified": "oups"})
print(result)

```

## Installing 

```
pip install dictgest
```