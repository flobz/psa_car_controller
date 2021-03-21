from __future__ import annotations

from typing import List

from geojson import Feature, FeatureCollection, MultiLineString

from Car import Cars, Car
from MyLogger import logger
from trip_parser import TripParser
from web.db import get_db


class Points():
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def list(self):
        return self.latitude, self.longitude


class Trip:
    def __init__(self):
        self.start_at = None
        self.end_at = None
        self.positions: List[Points] = []
        self.speed_average = None
        self.consumption = 0
        self.consumption_km = 0
        self.consumption_fuel = 0
        self.consumption_fuel_km = 0
        self.distance = None
        self.duration = None
        self.mileage = None
        self.car: Car = None

    def add_points(self, latitude, longitude):
        self.positions.append(Points(latitude, longitude))

    def set_consumption(self, diff_level: float) -> float:
        if self.distance is None:
            raise ValueError("Distance not set")
        if diff_level < 0:
            logger.debugv("trip has negative consumption")
            diff_level = 0
        self.consumption = diff_level * self.car.battery_power/100
        self.consumption_km = 100 * self.consumption / self.distance  # kw/100 km
        return self.consumption_km

    def set_fuel_consumption(self, consumption) -> float:
        if self.distance is None:
            raise ValueError("Distance not set")
        if consumption < 0:
            logger.debugv("trip has negative fuel consumption")
        self.consumption_fuel = round(consumption, 2)  # L
        self.consumption_fuel_km = round(100 * self.consumption_fuel / self.distance, 2)  # L/100 km
        return self.consumption_fuel_km

    def get_consumption(self):
        return {
            'date': self.start_at,
            'consumption': self.consumption_km,
        }

    def get_consumption_fuel(self):
        return {
            'date': self.start_at,
            'consumption': self.consumption_fuel_km,
        }

    def to_geojson(self):
        multi_line_string = MultiLineString(tuple(map(list, self.positions)))
        return Feature(geometry=multi_line_string, properties={"start_at": self.start_at, "end_at": self.end_at,
                                                               "average speed": self.speed_average,
                                                               "average consumption": self.consumption_km,
                                                               "average consumption fuel": self.consumption_fuel_km})

    def get_info(self):
        res = {"start_at": self.start_at.astimezone(None).strftime("%x %X"),
               "end_at": self.end_at.astimezone(None).strftime("%x %X"), "duration": self.duration * 60,
               "speed_average": self.speed_average, "consumption_km": self.consumption_km,
               "consumption_fuel_km": self.consumption_fuel_km, "distance": self.distance, "mileage": self.mileage}
        return res


class Trips(list):
    def __init__(self, *args):
        list.__init__(self, *args)

    def to_geo_json(self):
        feature_collection = FeatureCollection(self)
        return feature_collection

    def get_long_trips(self):
        res = []
        for tr in self:
            if tr.consumption > 1.8:
                res.append({"speed": tr.speed_average, "consumption_km": tr.consumption_km, "date": tr.start_at,
                            "consumption": tr.consumption})
        return res

    def check_and_append(self,tr:Trip):
        if tr.consumption_km <= tr.car.max_elec_consumption and tr.consumption_fuel_km <= tr.car.max_fuel_consumption:
            self.append(tr)
            return True
        logger.debugv("trip discarded")
        return False

    @staticmethod
    def get_trips(vehicles_list: Cars) -> dict[str, Trips]:
        conn = get_db()
        vehicles = conn.execute(
            "SELECT DISTINCT vin FROM position;").fetchall()
        trips_by_vin = {}
        for vin in vehicles:
            trips = Trips()
            vin = vin[0]
            res = conn.execute('SELECT * FROM position WHERE VIN=? ORDER BY Timestamp', (vin,)).fetchall()
            if len(res) > 1:
                car = vehicles_list.get_car_by_vin(vin)
                assert car is not None
                trip_parser = TripParser(car)
                start = res[0]
                end = res[1]
                tr = Trip()
                # for debugging use this line res = list(map(dict,res))
                for x in range(0, len(res) - 2):
                    logger.debugv("%s mileage:%.1f level:%s level_fuel:%s",
                                  res[x]['Timestamp'], res[x]['mileage'], res[x]['level'], res[x]['level_fuel'])
                    next_el = res[x + 2]
                    distance = end["mileage"] - start["mileage"]
                    duration = (end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600
                    try:
                        speed_average = distance / duration
                    except ZeroDivisionError:
                        speed_average = 0
                    restart_trip = False
                    if trip_parser.is_refuel(start, end, distance ):
                        restart_trip = True
                    elif speed_average < 0.2 and duration > 0.05:
                        restart_trip = True
                        logger.debugv("low speed detected")
                    if restart_trip:
                        start = end
                        tr = Trip()
                        logger.debugv("restart trip at %s mileage:%.1f level:%s level_fuel:%s",
                                      start['Timestamp'], start['mileage'], start['level'], start['level_fuel'])
                    else:
                        distance = next_el["mileage"] - end["mileage"]  # km
                        duration = (next_el["Timestamp"] - end["Timestamp"]).total_seconds() / 3600
                        try:
                            speed_average = distance / duration
                        except ZeroDivisionError:
                            speed_average = 0
                        end_trip = False
                        if trip_parser.is_refuel(end, next_el, distance):
                            end_trip = True
                        elif speed_average < 0.2 and duration > 0.05:
                            # (distance == 0 and duration > 0.08) or duration > 2 or
                            # check the speed to handle missing point
                            end_trip = True
                            logger.debugv("low speed detected")
                        elif duration > 2:
                            end_trip = True
                            logger.debugv("too much time detected")
                        elif x == len(res) - 3:  # last record detected
                            # think if add point is needed
                            end = next_el
                            end_trip = True
                            logger.debugv("last position found")
                        if end_trip:
                            logger.debugv("stop trip at %s mileage:%.1f level:%s level_fuel:%s",
                                          end['Timestamp'], end['mileage'], end['level'], end['level_fuel'])
                            tr.distance = end["mileage"] - start["mileage"]  # km
                            if tr.distance > 0:
                                tr.start_at = start["Timestamp"]
                                tr.end_at = end["Timestamp"]
                                tr.add_points(end["longitude"], end["latitude"])
                                tr.duration = (end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600
                                tr.speed_average = tr.distance / tr.duration
                                diff_level, diff_level_fuel = trip_parser.get_level_consumption(start, end)
                                tr.car = car
                                if diff_level != 0:
                                    tr.set_consumption(diff_level)# kw
                                if diff_level_fuel != 0:
                                    tr.set_fuel_consumption(diff_level_fuel)
                                tr.mileage = end["mileage"]
                                logger.debugv("Trip: %s -> %s %.1fkm %.2fh %.0fkm/h %.2fkWh %.2fkWh/100km %.2fL "
                                              "%.2fL/100km %.1fkm",
                                              tr.start_at, tr.end_at, tr.distance, tr.duration,
                                              tr.speed_average, tr.consumption, tr.consumption_km,
                                              tr.consumption_fuel, tr.consumption_fuel_km, tr.mileage)
                                # filter bad value
                                trips.check_and_append(tr)
                            start = next_el
                            tr = Trip()
                        else:
                            tr.add_points(end["longitude"], end["latitude"])
                    end = next_el
                trips_by_vin[vin] = trips
        return trips_by_vin
