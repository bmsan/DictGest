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
class Article:
    author: str
    title: str
    content: str


# Arguments passed to Route can be strings or dictgest.Path
article_api1 = Route(title="headline", content="details/content")

# New Routing for a new dict structure
article_api2 = Route(title="news_title", content="full_article")


article1 = from_dict(Article, news_api1_data, routing=article_api1)
article2 = from_dict(Article, news_api2_data, routing=article_api2)

print(article1)
print(article2)
