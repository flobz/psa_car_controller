from typing import List

from dateutil.tz import tzlocal
from geojson import Feature, Point, FeatureCollection, MultiLineString
from geojson import dumps as geo_dumps


class Points():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def list(self):
        return self.latitude, self.longitude


class Trips(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def to_geo_json(self):
        feature_collection = FeatureCollection(self)
        return feature_collection


class Trip:
    def __init__(self):
        self.start_at = None
        self.end_at = None
        self.positions: List[Points] = []
        self.speed_average = None
        self.consumption = None
        self.consumption_km = None
        self.distance = None
        self.duration = None

    def add_points(self, longitude, latitude):
        self.positions.append(Points(longitude, latitude))

    def get_consumption(self):
        return {
            'date': self.start_at,
            'consumption': self.consumption_km,
        }

    def to_geojson(self):
        multi_line_string = MultiLineString(tuple(map(list, self.positions)))
        return Feature(geometry=multi_line_string, properties={"start_at": self.start_at, "end_at": self.end_at,
                                                               "average speed": self.speed_average,
                                                               "average consumption": self.consumption_km})

    def get_info(self):
        res = {"start_at": self.start_at.astimezone(None).strftime("%x %X"), "end_at": self.end_at.astimezone(None).strftime("%x %X"), "duration": self.duration*60,
               "speed_average": self.speed_average, "consumption_km": self.consumption_km, "distance": self.distance}
        return res
