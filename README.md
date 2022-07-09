# DictGest - Python Dictionary Ingestion
![](https://github.com/bmsan/DictGest/blob/main/docs/source/dictgest_logo.jpg)

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=bmsan_DictGest&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=bmsan_DictGest)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=bmsan_DictGest&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=bmsan_DictGest)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=bmsan_DictGest&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=bmsan_DictGest)
[![Code Coverage](https://codecov.io/gh/bmsan/dictgest/branch/main/graph/badge.svg?token=WHTIAW8C85)](https://codecov.io/gh/bmsan/dictgest)
[![CI status](https://github.com/bmsan/dictgest/workflows/CI/badge.svg)](https://github.com/bmsan/dictgest/actions?queryworkflow%3ACI+event%3Apush+branch%3Amain)
[![Docs](https://readthedocs.org/projects/dictgest/badge/?version=latest)](https://readthedocs.org/projects/dictgest)
![MYPY](https://img.shields.io/badge/mypy-type%20checked-green)
![Pylint](https://img.shields.io/badge/Pylint-10.00/10-green)
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
The keys names in the source dictionary might not match the destionation class attribute names. 
Also the source dictionary might have a nested structure different than our desired structure.

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

There can be cases where Annotating the type hints of the target class is not desired by the user or when mapping to multiple APIs might be required.
For these cases look at examples 6 & 7 for an alternate solution.

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
Sometimes we might want to apply custom transforms to some fields when extracting the data from the dictionary.
In this example we want to read the total number of votes, but in the dictionary source we only have two partial values: the positive and negative number of votes.

We apply a custom transform to get our desired data, using the `extractor`  argument of `dictgest.Path`

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

In some cases we might want to employ a custom conversion for a certain datatype.

```py
from dataclasses import dataclass
from dictgest import default_convertor, from_dict

# Get any already registered bool convertor
default_bool_conv = default_convertor.get_convertor(bool)

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

## Example 6: Populating the same structure from multiple different dict formats (multiple APIs)

There are cases where you might read information from multiple heterogenous APIs and you might want to convert them all to the same structure.

Previously we have annotated fields( using typing.Annotation hint ) with Path eg: ` name: Annotated[str, Path('article')] `. This works well for a single conversion mapping.

For this current scenario we are going to decouple the class from the Routing.

Previously single mapping scenario:
```py
@dataclass
class Article:
    author: str
    title: Annotated[str, Path("headline")]
    content: Annotated[str, Path("details/content")]

```


But now we have 2 API news sources

```py
data_from_api1 = {
    "author": "H.O. Ward"
    "headline" : "Top 10 Python extensions", 
    "other_fields" : ...,
    "details": {
        "content": "Here are the top 10...",
        "other_fields": ...
         }
    }

data_from_api2 = {
    "author": "G.O. Gu" 
    "news_title" : "Vscode gets a new facelift", 
    "other_fields" : ...,
    "full_article": "Yesterday a new version ...",
    }


}
```

We are going to use `dictgest.Route` to define multiple standalone routes.

Our previous example becomes:
```py
@dataclass
class Article:
    author: str
    title: str # Path annotations are decoupled
    content: str

# Routing equivalent to previous example
article_api1 = Route(title="headline", content="details/content")

# New Routing for a new dict structure
article_api2 = Route(title="news_title", content="full_article")


article1 = from_dict(Article, data_from_api1, routing=article_api1)
article2 = from_dict(Article, data_from_api2, routing=article_api2)
```


The full working example can be found in the [examples folder](https://github.com/bmsan/DictGest/blob/main/examples/news_multi_example.py)


## Example 7: Populating multiple structures from multiple different dict formats (multiple APIs)
The previous example treated the mapping of a single Class to multiple formats.
Now we'll see how to map multiple Classes to multiple formats.

```py
@dataclass
class ArticleStats:
    views: int
    num_comments: int


@dataclass
class Article:
    author: str
    title: str
    content: str
    stats: ArticleStats
```


Previously we used `dictgest.Route` to pass the routing corresponding to a single class.

To do the same but for multiple classes we can pass a dictionary of routes
` {Cls1: Cls1Route, Cls2: Cls2Route,...} `


```py
api1_routing = {
    Article: Route(
        title="headline",
        content="details/content",
        stats="",  # Give the whole dictionary to ArticleStats for conversion
    ),
    ArticleStats: Route(views="details/views", num_comments="details/comments"),
}

api2_routing = {
    Article: Route(title="news_title", content="full_article", stats=""),
    ArticleStats: Route(num_comments="comments"),
}

```

And then call

```py
article1 = from_dict(Article, news_api1_data, routing=api1_routing)
article2 = from_dict(Article, news_api2_data, routing=api2_routing)

```

The full working example can be found in the [examples folder](https://github.com/bmsan/DictGest/blob/main/examples/news_multi_adv_example.py)



## Installing 

```
pip install dictgest
```

## Contributing

First off, thanks for taking the time to contribute! Contributions are what makes the open-source community such an amazing place to learn, inspire, and create. Any contributions you make will benefit everybody else and are **greatly appreciated**.

## Support

Reach out to the maintainer at one of the following places:
- [Github issues](https://github.com/bmsan/DictGest/issues)
- [Discord](https://discord.gg/yBb99rxBUZ)


## License

This project is licensed under the **MIT license**. Feel free to edit and distribute this template as you like.

See [LICENSE](LICENSE) for more information.

## Acknowledgements

- Thanks [Dan Oneata](https://github.com/danoneata) for the discussions related to usecases and API.
