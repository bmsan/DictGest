# DictGest - Python Dictionary Ingestion

[![Code Coverage](https://codecov.io/gh/bmsan/dictgest/branch/main/graph/badge.svg)](https://codecov.io/gh/bmsan/dictgest)
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

## Example 1: Trivial Example
The first most basic and trivial example is ingesting a dictionary that has extra data not of interest

![](https://github.com/bmsan/DictGest/blob/main/docs/source/ex1.png?raw=true)

```python
car = from_dict(Car, dict_data)
```

## Example 2: Data mapping renaming & rerouting
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
@typecast
@dataclass
class Measurment:
    temp: float
    humidity: float


@typecast
class Sensor:
    def __init__(
        self, name: str, location: str, uptime: float, readings: list[Measurment]
    ):
        self.name = name
        self.location = location
        self.uptime = uptime
        self.readings = readings

    def __repr__(self):
        return str(self.__dict__)

```

![](https://github.com/bmsan/DictGest/blob/main/docs/source/ex3.png?raw=true)

The conversions shown above were enabled by setting the `@typecast` decorator for the targetted classes.

The full working example can be found in the [examples folder](https://github.com/bmsan/DictGest/blob/main/examples/typeconvert_example.py)



## Installing 

```
pip install dictgest
```