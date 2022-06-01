from dataclasses import dataclass
from typing import Annotated
from dictgest import from_dict, Path


news_api_data = {
    "author": "H.O. Ward",
    "headline": "Will statically typed python become a thing?",
    "details": {
        "content": "Over the past 10 years ...[+]",
        "description": "Statically typing is getting ...[+]",
        "views": 32,
        "comments": 2,
    },
    "seo": {"tags": ["python", "programming"], "kwrds": ["guido", "python"]},
}


@dataclass
class Article:
    author: str
    title: Annotated[str, Path("headline")]
    content: Annotated[str, Path("details/content")]


class ArticleMeta:
    def __init__(
        self,
        description: Annotated[str, Path("details/description")],
        tags: Annotated[str, Path("seo/tags")],
        keywords: Annotated[str, Path("seo/kwrds")],
    ):
        ...


@dataclass
class ArticleStats:
    views: Annotated[int, Path("details/views")]
    num_comments: Annotated[int, Path("details/comments")]


article = from_dict(Article, news_api_data)
meta = from_dict(ArticleMeta, news_api_data)
stats = from_dict(ArticleStats, news_api_data)
print(article)
print(meta)
print(stats)
