[![Code Coverage](https://codecov.io/gh/bmsan/dataclass-serdes/branch/master/graph/badge.svg)](https://codecov.io/gh/bmsan/dataclass-serdes)

[![CI status](https://github.com/bmsan/dataclass-serdes/workflows/CI/badge.svg)](https://github.com/bmsan/dataclass-serdes/actions?queryworkflow%3ACI+event%3Apush+branch%3Amain)
```python
class Car:
    def __init__(self, name, year,
                 color, num_seats=4, 
                 steering_side='left'):
        ...


car = from_dict(Car, {
                        'name': 'Honda', 
                        'year': 2022
                        'color': 'red',
                        // num_seats is missing
                       
                        'steering_side' : right,
                        // we can have extra atributes that will be ignored
                        'completed_by' : 'H.O. Ward',
                        'completed_at' '2022/02/02'
                      })

@dataclass
class ArticleV2:
  author: str
  title: str
  views: int 
  num_comments: int  


// Location Mapping

@typecheck
@typecast
@dataclass
class ArticleV3:
  # This will be extracted from the author field
  author: str
  # headline renamed to title
  title:  Annotated[str, Path('headline')]  
  # different path + rename
  description: Annotated[str, Path('content/shortVersion')]
  # Transform the data 
  total_votes: Annotated[str, Path('stats', extractor=compute_votes)]


def compute_votes(stats: dict):
  return stats['pozitive_votes'] + stats['negative_votes']


....
@typeconvert

````
