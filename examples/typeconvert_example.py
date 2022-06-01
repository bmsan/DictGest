from dataclasses import dataclass
from dictgest.serdes import from_dict, typecast


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


data = {
    "name": "sigma sensor",
    "location": "district 9",
    "uptime": "39",
    "readings": [
        {"temp": "20", "humidity": "0.4"},
        {"temp": "25", "humidity": "0.45"},
        {"temp": "30", "humidity": "0.39"},
    ],
}


sensor = from_dict(Sensor, data)
print(sensor)
