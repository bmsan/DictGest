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
        self.title = title
        self.total_votes = total_votes

    def __repr__(self):
        return str(self.__dict__)


article_data = {
    "title": "Python 4.0 will...",
    "details": {"votes": {"positive": "245", "negative": "30"}},
}


votes = from_dict(Votes, article_data)
print(votes)
