from dataclasses import dataclass
from datetime import datetime
from dictgest.serdes import from_dict, typecast


@typecast
@dataclass
class Measurment:
    temp: float
    humidity: float
    date: datetime


@typecast
class Sensor:
    def __init__(
        self,
        name: str,
        location: str,
        uptime: float,
        charging: bool,
        readings: list[Measurment],
    ):
        self.name = name
        self.location = location
        self.uptime = uptime
        self.charging = charging
        self.readings = readings

    def __repr__(self):
        return str(self.__dict__)


data = {
    "name": "sigma sensor",
    "location": "district 9",
    "uptime": "39",
    "charging": "yes",
    "readings": [
        {"temp": "20", "humidity": "0.4", "date": "2022/06/12"},
        {"temp": "25", "humidity": "0.45", "date": "July 03 2021"},
        {"temp": "30", "humidity": "0.39", "date": "2020-05-03"},
    ],
}


sensor = from_dict(Sensor, data)
print(sensor)
