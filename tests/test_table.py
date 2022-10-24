import datetime
from typing import Annotated, Any, Protocol, runtime_checkable
import pytest
from dataclasses import dataclass
from dictgest import from_dict, typecast
from dictgest import Path
import dictgest as dg
from .utils import check_fields


def test_single_item():
    @typecast
    class SenzorData:
        def __init__(
            self,
            timestamps: list[datetime.datetime],
            temperatures: list[float],
            humidity: list[float],
        ) -> None:
            self.timestamps = timestamps
            self.temperatures = temperatures
            self.humidity = humidity

    header = ["humidity", "temperatures", "timestamps"]
    table_data = [
        [0.4, 7.4, "1Dec2022"],
        [0.6, 5.4, "2Dec2022"],
    ]

    ref = {
        "humidity": [0.4, 0.6],
        "temperatures": [7.4, 5.4],
        "timestamps": [
            datetime.datetime(year=2022, month=12, day=1),
            datetime.datetime(year=2022, month=12, day=2),
        ],
    }

    result = dg.table_to_item(SenzorData, table_data, header)
    check_fields(result, ref)
    result = dg.from_table(SenzorData, table_data, header)

    with pytest.raises(ValueError):
        result = dg.table_to_item(SenzorData, table_data, header, transpose=True)
        list(result)

    table_data = [
        [7.4, 5.4],
        ["1Dec2022", "2Dec2022"],
        [0.4, 0.6],
    ]

    header = ["temperatures", "timestamps", "humidity"]
    result = dg.table_to_item(SenzorData, table_data, header, transpose=True)
    check_fields(result, ref)
    result = dg.from_table(SenzorData, table_data, header, transpose=True)
    check_fields(result, ref)

    with pytest.raises(ValueError):
        result = dg.table_to_item(SenzorData, table_data, header)
        list(result)


def test_multi_item():
    @typecast
    class SenzorData:
        def __init__(
            self,
            timestamp: datetime.datetime,
            temperature: float,
            humidity: float,
        ) -> None:
            self.timestamp = timestamp
            self.temperature = temperature
            self.humidity = humidity

    refs = [
        {
            "humidity": 0.4,
            "temperature": 7.4,
            "timestamp": datetime.datetime(year=2022, month=12, day=1),
        },
        {
            "humidity": 0.6,
            "temperature": 5.4,
            "timestamps": datetime.datetime(year=2022, month=12, day=2),
        },
    ]

    header = ["humidity", "temperature", "timestamp"]
    table_data = [
        [0.4, 7.4, "1Dec2022"],
        [0.6, 5.4, "2Dec2022"],
    ]

    result = dg.table_to_items(SenzorData, table_data, header)
    for res, ref in zip(result, refs):
        check_fields(res, ref)

    result = dg.from_table(SenzorData, table_data, header, item_per_row=True)
    for res, ref in zip(result, refs):
        check_fields(res, ref)

    table_data = [
        [7.4, 5.4],
        ["1Dec2022", "2Dec2022"],
        [0.4, 0.6],
    ]

    header = ["temperature", "timestamp", "humidity"]
    result = dg.table_to_items(SenzorData, table_data, header, transpose=True)
    for res, ref in zip(result, refs):
        check_fields(res, ref)

    result = dg.from_table(
        SenzorData, table_data, header, transpose=True, item_per_row=True
    )
    for res, ref in zip(result, refs):
        check_fields(res, ref)

    with pytest.raises(ValueError):
        result = dg.table_to_items(SenzorData, table_data, header)
        list(result)
