import logging
from typing import Dict

from geojson import FeatureCollection

from psa_car_controller.common.mylogger import CustomLogger
from psa_car_controller.psacc.application.trip_parser import TripParser

from psa_car_controller.psacc.model.trip import Trip
from psa_car_controller.psacc.model.car import Cars
from psa_car_controller.psacc.repository.db import Database

logger = CustomLogger.getLogger(__name__)


class Trips(list):
    def __init__(self, *args):
        list.__init__(self, *args)
        self.trip_num = 1

    def to_geo_json(self):
        feature_collection = FeatureCollection(self)
        return feature_collection

    def get_trips_as_dict(self):
        return [trip.get_info() for trip in self]

    def get_distance(self):
        return self[-1].mileage - self[0].mileage

    def check_and_append(self, trip: Trip):
        if trip.consumption_km <= trip.car.max_elec_consumption and \
                trip.consumption_fuel_km <= trip.car.max_fuel_consumption:
            trip.id = self.trip_num
            self.trip_num += 1
            self.append(trip)
            return True
        logger.debugv("trip discarded")
        return False

    @staticmethod  # noqa: MC0001
    def get_trips(vehicles_list: Cars) -> Dict[str, "Trips"]:
        # pylint: disable=too-many-locals,too-many-statements,too-many-nested-blocks,too-many-branches
        conn = Database.get_db()
        vehicles = conn.execute("SELECT DISTINCT vin FROM position;").fetchall()
        trips_by_vin = {}
        for vin in vehicles:
            trips = Trips()
            vin = vin[0]
            res = conn.execute('SELECT Timestamp, VIN, longitude, latitude, mileage, level, moving, temperature, '
                               'level_fuel, altitude FROM position WHERE VIN=? '
                               'AND mileage IS NOT NULL ORDER BY Timestamp', (vin,)).fetchall()
            if len(res) > 1:
                car = vehicles_list.get_car_by_vin(vin)
                assert car is not None
                trip_parser = TripParser(car)
                start = res[0]
                end = res[1]
                trip = Trip()
                # for debugging use this line res = list(map(dict,res))
                for x in range(0, len(res) - 2):
                    if logger.isEnabledFor(logging.DEBUG):  # reduce execution time if debug disabled
                        logger.debugv("%s mileage:%.1f level:%s level_fuel:%s",
                                      res[x]['Timestamp'], res[x]['mileage'], res[x]['level'], res[x]['level_fuel'])
                    next_point = res[x + 2]
                    distance = 0
                    try:
                        distance = end["mileage"] - start["mileage"]
                    except TypeError:
                        logger.debug("Bad mileage value in DB")
                    duration = (end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600
                    try:
                        speed_average = distance / duration
                    except ZeroDivisionError:
                        speed_average = 0

                    if TripParser.is_low_speed(speed_average, duration) or trip_parser.is_refuel(start, end, distance):
                        start = end
                        trip = Trip()
                        logger.debugv("restart trip at {0[Timestamp]} mileage:{0[mileage]:.1f} level:{0[level]}"
                                      " level_fuel:{0[level_fuel]}", start, style='{')
                    else:
                        distance = next_point["mileage"] - end["mileage"]  # km
                        duration = (next_point["Timestamp"] - end["Timestamp"]).total_seconds() / 3600
                        try:
                            speed_average = distance / duration
                        except ZeroDivisionError:
                            speed_average = 0
                        end_trip = False
                        if trip_parser.is_refuel(end, next_point, distance) or \
                                TripParser.is_low_speed(speed_average, duration):
                            end_trip = True
                        elif duration > 2:
                            end_trip = True
                            logger.debugv("too much time detected")
                        elif x == len(res) - 3:  # last record detected
                            # think if add point is needed
                            end = next_point
                            end_trip = True
                            logger.debugv("last position found")
                        if end_trip:
                            logger.debugv("stop trip at {0[Timestamp]} mileage:{0[mileage]:.1f} level:{0[level]}"
                                          " level_fuel:{0[level_fuel]}", end, style='{')
                            trip.distance = end["mileage"] - start["mileage"]  # km
                            if trip.distance > 0:
                                trip.start_at = start["Timestamp"]
                                trip.end_at = end["Timestamp"]
                                trip.add_points(end["latitude"], end["longitude"])
                                if end["temperature"] is not None and start["temperature"] is not None:
                                    trip.add_temperature(end["temperature"])
                                trip.duration = (end["Timestamp"] - start["Timestamp"]).total_seconds() / 3600
                                trip.speed_average = trip.distance / trip.duration
                                diff_level, diff_level_fuel = trip_parser.get_level_consumption(start, end)
                                trip.set_altitude_diff(start["altitude"], end["altitude"])
                                trip.car = car
                                if diff_level != 0:
                                    trip.set_consumption(diff_level)  # kw
                                if diff_level_fuel != 0:
                                    trip.set_fuel_consumption(diff_level_fuel)
                                trip.mileage = end["mileage"]
                                logger.debugv("Trip: {0.start_at} -> {0.end_at} {0.distance:.1f}km {0.duration:.2f}h "
                                              "{0.speed_average:.0f}km/h {0.consumption:.2f}kWh "
                                              "{0.consumption_km:.2f}kWh/100km {0.consumption_fuel:.2f}L "
                                              "{0.consumption_fuel_km:.2f}L/100km {0.mileage:.1f}km", trip, style="{")
                                # filter bad value
                                trips.check_and_append(trip)
                            start = next_point
                            trip = Trip()
                        else:
                            trip.add_points(end["latitude"], end["longitude"])
                    end = next_point
                trips_by_vin[vin] = trips
        conn.close()
        return trips_by_vin
