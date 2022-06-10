import inspect
from typing import Any, Callable, Iterable, Mapping, Optional, Union

from dictgest.utils import flatten


class Path:
    """Data type annotation for class attributes that can signal:
      - renaming: maping a dictionary field to an attribute with a different name
      - rerouting: mapping a nested dictionary field to a class attribute
      - Setting a default data converter for the field

    Its is used in conjunction with Pythons ``Typing.Annotated`` functionality

    .. code-block:: python

        class Model:
            def __init__(self,
                        // the module will extract the 'field1' key
                        field1,
                        // the module will extract the 'name' key
                        field2 : Annotated[str, Path('name')]
                        // the module will extract the ['p1']['p2']['val'] field
                        field3 : Annotated[str, Path('p1/p2/val')]
                        )

    """

    def __init__(self, path: str, extractor: Callable = None, flatten_en=True) -> None:
        """

        Parameters
        ----------
        path
            Extraction path(key/keys) from dictionary.
            Eg: path='name1' will map the annotated field to a dictionary key 'name1'
            Eg: path='p1/p2/name2' will map the annotated field to nested_data['p1']['p2']['name2']
        extractor, optional
            Callable to extract/convert the data from the specified path, by default None
        flatten_en, optional
            In case the path contains an element which is a list, flatten it's elements

            Eg: data = {'a': [
                              [{'b': 1}, {'b': 2}],
                              [{'b': 3}]
                            ]}
            path='a/b' with flatten_en would result in the extraction of [1, 2, 3]
        """

        self.path = path
        self.parts = path.split("/")
        self.extractor = extractor
        self.flatten_en = flatten_en

    @staticmethod
    def _wildcard_extract(data: Iterable, part: str):
        if not isinstance(data, (list, tuple)):
            raise TypeError()
        if "{" in part:
            name, val = part.split("{", 1)[1].split("}", 1)[0].split("=")
            data = [el for el in data if name in el and str(el[name]) == val]
        return data

    def _iterable_extract(self, data: Iterable, part: str) -> list:
        data = [o[part] for o in data if part in o]
        if self.flatten_en:
            data = flatten(data)
        return data

    def extract(self, data: dict[str, Any]):
        """Extract element from dictionary data from the configured path.

        Parameters
        ----------
        data
            Dictionary from which to extract the targeted value

        Returns
        -------
            Extracted value

        """
        for part in self.parts:

            if part.startswith("*"):
                data = Path._wildcard_extract(data, part)
            elif isinstance(data, (list, tuple)):
                data = self._iterable_extract(data, part)

            elif part != "":
                data = data[part]
        if self.extractor is not None:
            data = self.extractor(data)
        return data

    def get(self, data: dict, default):
        """`extract` with default value in case of failure"""
        try:
            return self.extract(data)
        except KeyError:
            return default


class Route:
    """A Template/Chart describing the routing between a class and dictionary

    Initialized with keyword arguments containing the mapping.
    - The keys correspond to the destination field names.
    - The values correspond to the extraction path. They can be of type `value` or type `Path`

    Example
    --------
        Route(  title="headline",
                category="description/category",
                content=Path("description/content"),
                votes=Path("meta/traffic", extractor=votes_extreactor)
                )
    """

    def __init__(self, **kwargs: dict[str, Union[Path, str]]) -> None:
        """kwargs:
        - keys : destination mapping names
        - values: dictionary path.
        """
        if not kwargs:
            raise ValueError("Did not pass any parameters to route")
        self.mapping = kwargs
        for key, val in kwargs.items():
            if isinstance(val, str):
                self.mapping[key] = Path(val)
            elif not isinstance(val, Path):
                raise TypeError(
                    f"Encountered field of type: {type(val)}, expecting Path or str"
                )

    def __getitem__(self, key):
        return self.mapping[key] if key in self.mapping else None

    def check_type(self, dtype: type):
        """
        Check if the dtype is compatible with the Route
        """
        params = inspect.signature(dtype).parameters
        self.check_params(params)

    def check_params(self, params: Iterable[str]):
        """Chek if the parameter names are compatible with the Route"""
        params = set(params)
        for key in self.mapping:
            if key not in params:
                raise ValueError(
                    f"Route containing field {key}, but not present in target class "
                )


class Chart:
    """A chart is a collection of routes mapped to classes.
    A chart describes the way a dictionary ingestion should happen,
    when multiple different classes will be converted.
    """

    def __init__(self, routes: Mapping[type, Route]):
        if not isinstance(routes, Mapping):
            raise TypeError(f"Expected a Mapping type, received {type(routes)}")
        self.routes = routes
        self.typecast: Optional[Callable] = None
        self.check()

    def check(self):
        """Check the validity of the chart.
        A chart can be invalid if the configured routes cannot be mapped to targeted objects.
        Eg: one of the routes contains a field that is not present in the data type
        """
        for dtype, route in self.routes.items():
            route.check_type(dtype)

    def __contains__(self, key):
        return key in self.routes

    def __getitem__(self, key):
        return self.routes[key]
