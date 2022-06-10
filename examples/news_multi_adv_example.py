from dataclasses import dataclass
from typing import Annotated
from dictgest import from_dict, Path, Route


news_api1_data = {
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

news_api2_data = {
    "author": "H. Gogu",
    "news_title": "Best python extensions",
    "full_article": "Let's explore the best extensions for python",
    "views": 32,
    "comments": 2,
}


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


article1 = from_dict(Article, news_api1_data, routing=api1_routing)
article2 = from_dict(Article, news_api2_data, routing=api2_routing)

print(article1)
print(article2)
