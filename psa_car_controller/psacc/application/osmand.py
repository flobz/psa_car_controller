import logging
from datetime import datetime

import requests

from psa_car_controller.psacc.model.car import Car

logger = logging.getLogger(__name__)
TIMEOUT_IN_S = 10


class OsmAndApi:
    def __init__(self, server_uri: str = None, osmand_enable_vin=None):
        if osmand_enable_vin is None:
            osmand_enable_vin = []
        self.__server_uri = server_uri
        self.osmand_enable_vin = set(osmand_enable_vin)
        self.proxies = None

    def enable_osmand(self, vin, enable):
        if enable:
            self.osmand_enable_vin.add(vin)
        else:
            self.osmand_enable_vin.discard(vin)

    def call(self, car: Car, ext_temp: float = None):
        try:
            if car.vin in self.osmand_enable_vin:
                if self.__server_uri is None:
                    logger.debug("osmandapi: No Server URI set")
                    return False

                if not car.has_fuel() and not car.has_battery():
                    logger.debug("Neither fuel nor battery available")
                    return False

                data = {
                    "id": car.get_osmand_id(),
                    "timestamp": int(datetime.timestamp(car.status.last_position.properties.updated_at)),
                    "is_parked": not bool(car.status.is_moving()),
                    "odometer": car.status.timed_odometer.mileage * 1000,
                    "speed": getattr(car.status.kinetic, "speed", 0.0),
                    "lat": car.status.last_position.geometry.coordinates[1],
                    "lon": car.status.last_position.geometry.coordinates[0],
                    "altitude": car.status.last_position.geometry.coordinates[2]
                }
                if car.has_fuel:
                    fuel = car.status.get_energy('Fuel')
                    data["fuel"] = fuel.level
                if car.has_battery():
                    energy = car.status.get_energy('Electric')
                    if energy.battery and energy.battery.health:
                        data["soh"] = energy.battery.health.resistance
                    data["soc"] = energy.level
                    data["batt"] = energy.level
                    data["power"] = energy.consumption
                    data["current"] = car.status.battery.current
                    data["voltage"] = car.status.battery.voltage
                    data["is_charging"] = energy.charging.status == "InProgress"
                    data['est_battery_range'] = energy.autonomy

                if ext_temp is not None:
                    data["ext_temp"] = ext_temp

                response = requests.request("POST", self.__server_uri, params=data, proxies=self.proxies,
                                            verify=self.proxies is None, timeout=TIMEOUT_IN_S)
                logger.debug(response.text)
                try:
                    return response.status_code == 200
                except (KeyError):
                    logger.error("Bad response from OsmAnd API: %s", response.text)
                    return False
        except (AttributeError, IndexError, ValueError):
            logger.exception("osmandapi:")
        return False

    def __iter__(self):
        yield "osmand_enable_vin", list(self.osmand_enable_vin)
        yield "server_uri", self.__server_uri
