# flake8: noqa
import json
import os
import unittest
from datetime import datetime, timedelta

from pytz import UTC

import libs.config
from psa_connectedcar import ApiClient
import psa_connectedcar as psacc
import reverse_geocode
from libs.car import Car, Cars
from libs.charging import Charging
from libs.elec_price import ElecPrice
from my_psacc import MyPSACC
from ecomix import Ecomix
from libs.car_model import CarModel
from mylogger import my_logger
from otp.otp import load_otp, save_otp
from charge_control import ChargeControls
from test.utils import DATA_DIR, record_position, latitude, longitude, date0, date1, date2, date3, record_charging, \
    vehicule_list, get_new_test_db, get_date, date4
from trip import Trips
from libs.utils import get_temp, parse_hour, rate_limit, RateLimitException
from web.db import Database
from web.figures import get_figures, get_battery_curve_fig, get_altitude_fig
from deepdiff import DeepDiff



def compare_dict(result, expected):
    diff = DeepDiff(expected,  result)
    if diff != {}:
        raise AssertionError(str(diff))
    return True


dummy_value = 0


def callback_test():
    global dummy_value
    dummy_value += 1


class TestUnit(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.test_online = os.environ.get("TEST_ONLINE", "0") == "1"
        self.vehicule_list = vehicule_list

    def test_car(self):
        car1 = Car("VRAAAAAAA", "1sdfdksnfk222", "Peugeot", "208", 46, 0)
        car2 = Car("VR3UHZKX", "1sdfdksnfk222", "Peugeot")
        cars = Cars([car1, car2])
        cars.save_cars(name=DATA_DIR + "test_car.json")
        Cars.load_cars(name=DATA_DIR + "test_car.json")

    def test_otp_config(self):
        otp_config = load_otp(filename=DATA_DIR + "otp_test.bin")
        assert otp_config is not None
        save_otp(otp_config, filename=DATA_DIR + "otp_test2.bin")

    def test_mypsacc(self):
        if self.test_online:
            myp = MyPSACC.load_config("config.json")
            myp.refresh_token()
            myp.get_vehicles()
            car = myp.vehicles_list[0]
            myp.abrp.abrp_enable_vin.add(car.vin)
            res = myp.get_vehicle_info(myp.vehicles_list[0].vin)
            myp.abrp.call(car, 22.1)
            libs.config.Config().myp = myp
            libs.config.Config().save_config()
            assert isinstance(get_temp(str(latitude), str(longitude), myp.weather_api), float)

    def test_car_model(self):
        assert CarModel.find_model_by_vin("VR3UHZKXZL").name == "e-208"
        assert CarModel.find_model_by_vin("VR3UKZKXZM").name == "e-2008"
        assert CarModel.find_model_by_vin("VXKUHZKXZL").name == "corsa-e"

    def test_c02_signal_cache(self):
        start = datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=30)
        end = datetime.utcnow().replace(tzinfo=UTC)
        Ecomix._cache = {'FR': [[start - timedelta(days=1), 100],
                                [start + timedelta(minutes=1), 10],
                                [start + timedelta(minutes=2), 20],
                                [start + timedelta(minutes=3), 30]]}
        assert Ecomix.get_co2_from_signal_cache(start, end, "FR") == 20

    def test_c02_signal(self):
        if self.test_online:
            key = "d186c74bfbcd1da8"
            Ecomix.co2_signal_key = key
            def_country = "FR"
            Ecomix.get_data_from_co2_signal(latitude, longitude, def_country)
            res = Ecomix.get_co2_from_signal_cache(datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=5), datetime.now(), def_country)
            assert isinstance(res, float)

    def test_charge_control(self):
        charge_control = ChargeControls()
        charge_control.file_name = "test_charge_control.json"
        charge_control.save_config(force=True)

    def test_battery_curve(self):
        get_new_test_db()
        record_charging()
        res = Database.get_battery_curve(Database.get_db(), date0, date4, self.vehicule_list[0].vin)
        assert len(res) == 3

    def test_sdk(self):
        res = {
            'lastPosition': {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [9.65457, 49.96119, 21]},
                             'properties': {'updatedAt': '2021-03-29T05:16:10Z', 'heading': 126,
                                            'type': 'Estimated'}}, 'preconditionning': {
                'airConditioning': {'updatedAt': '2021-04-01T16:17:01Z', 'status': 'Disabled', 'programs': [
                    {'enabled': False, 'slot': 1, 'recurrence': 'Daily', 'start': 'PT21H40M',
                     'occurence': {'day': ['Sat']}}]}},
            'energy': [{'updatedAt': '2021-02-23T22:29:03Z', 'type': 'Fuel', 'level': 0},
                       {'updatedAt': '2021-04-01T16:17:01Z', 'type': 'Electric', 'level': 70, 'autonomy': 192,
                        'charging': {'plugged': True, 'status': 'InProgress', 'remainingTime': 'PT0S',
                                     'chargingRate': 20, 'chargingMode': 'Slow', 'nextDelayedTime': 'PT21H30M'}}],
            'createdAt': '2021-04-01T16:17:01Z',
            'battery': {'voltage': 99, 'current': 0, 'createdAt': '2021-04-01T16:17:01Z'},
            'kinetic': {'createdAt': '2021-03-29T05:16:10Z', 'moving': False},
            'privacy': {'createdAt': '2021-04-01T16:17:01Z', 'state': 'None'},
            'service': {'type': 'Electric', 'updatedAt': '2021-02-23T21:10:29Z'}, '_links': {'self': {
                'href': 'https://api.groupe-psa.com/connectedcar/v4/user/vehicles/myid/status'},
                'vehicles': {
                    'href': 'https://api.groupe-psa.com/connectedcar/v4/user/vehicles/myid'}},
            'timed.odometer': {'createdAt': None, 'mileage': 1107.1}, 'updatedAt': '2021-04-01T16:17:01Z'}
        api = ApiClient()
        status: psacc.models.status.Status = api._ApiClient__deserialize(res, "Status")
        geocode_res = reverse_geocode.search([(status.last_position.geometry.coordinates[:2])[::-1]])[0]
        assert geocode_res["country_code"] == "DE"
        get_new_test_db()
        car = Car("XX", "vid", "Peugeot")
        car.status = status
        myp = MyPSACC.load_config(DATA_DIR + "config.json")
        myp.record_info(car)
        assert "features" in json.loads(Database.get_recorded_position())
        # electric should be first
        assert car.status.energy[0].type == 'Electric'

    def test_record_position_charging(self):
        get_new_test_db()
        ElecPrice.CONFIG_FILENAME = DATA_DIR + "config.ini"
        car = self.vehicule_list[0]
        record_position()
        Database.add_altitude_to_db(Database.get_db())
        data = json.loads(Database.get_recorded_position())
        assert data["features"][1]["geometry"]["coordinates"] == [float(longitude), float(latitude)]
        trips = Trips.get_trips(self.vehicule_list)[car.vin]
        trip = trips[0]
        map(trip.add_temperature, [10, 13, 15])
        res = trip.get_info()
        assert compare_dict(res, {'consumption_km': 24.21052631578947,
                                  'start_at': date0,
                                  'consumption_by_temp': None,
                                  'positions': {'lat': [latitude], 'long': [longitude]},
                                  'duration': 40.0, 'speed_average': 28.5, 'distance': 19.0, 'mileage': 30.0,
                                  'altitude_diff': 2, 'id': 1, 'consumption': 4.6})

        Charging.elec_price = ElecPrice.read_config()
        start_level = 40
        end_level = 85
        Charging.record_charging(car, "InProgress", date0, start_level, latitude, longitude, None, "slow", 20, 60)
        Charging.record_charging(car, "InProgress", date1, 70, latitude, longitude, "FR", "slow", 20, 60)
        Charging.record_charging(car, "InProgress", date1, 70, latitude, longitude, "FR", "slow",20, 60)
        Charging.record_charging(car, "InProgress", date2, 80, latitude, longitude, "FR", "slow", 20, 60)
        Charging.record_charging(car, "Stopped", date3, end_level, latitude, longitude, "FR", "slow", 20, 60)
        chargings = Charging.get_chargings()
        co2 = chargings[0]["co2"]
        assert isinstance(co2, float)
        assert compare_dict(chargings, [{'start_at': date0,
                                         'stop_at': date3,
                                         'VIN': 'VR3UHZKX',
                                         'start_level': 40,
                                         'end_level': 85,
                                         'co2': co2,
                                         'kw': 20.7,
                                         'price': 3.84,
                                         'charging_mode': 'slow'}])
        print()
        assert get_figures(car)
        row = {"start_at": date0.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
               "stop_at": date3.strftime('%Y-%m-%dT%H:%M:%S.000Z'), "start_level": start_level, "end_level": end_level}
        assert get_battery_curve_fig(row, car) is not None
        assert get_altitude_fig(trip) is not None

    def test_fuel_car(self):
        get_new_test_db()
        ElecPrice.CONFIG_FILENAME = DATA_DIR + "config.ini"
        car = self.vehicule_list[1]
        Database.record_position(None, car.vin, 11, latitude, longitude, 22, date0, 40, 30, False)
        Database.record_position(None, car.vin, 20, latitude, longitude, 22, date1, 35, 29, False)
        Database.record_position(None, car.vin, 30, latitude, longitude, 22, date2, 30, 28, False)
        trips = Trips.get_trips(self.vehicule_list)
        res = trips[car.vin].get_trips_as_dict()
        assert compare_dict(res, [{'consumption_km': 6.947368421052632,
                                   'start_at': date0,
                                   'consumption_by_temp': None,
                                   'positions': {'lat': [latitude],
                                                'long': [longitude]},
                                   'duration': 40.0,
                                   'speed_average': 28.5,
                                   'distance': 19.0,
                                   'mileage': 30.0,
                                   'altitude_diff': 0,
                                   'id': 1,
                                   'consumption': 1.32,
                                   'consumption_fuel_km': 10.53}])

    def test_none_mileage(self):
        get_new_test_db()
        ElecPrice.CONFIG_FILENAME = DATA_DIR + "config.ini"
        car = self.vehicule_list[1]
        Database.record_position(None, car.vin, None, latitude, longitude, 22, get_date(1), 40, 30, False)
        Database.record_position(None, car.vin, None, latitude, longitude, 22, get_date(2), 35, 29, False)
        Database.record_position(None, car.vin, None, latitude, longitude, 22, get_date(3), 30, 28, False)
        start = get_date(4)
        end = get_date(6)
        Database.record_position(None, car.vin, 11, latitude, longitude, 22, start, 40, 30, False)
        Database.record_position(None, car.vin, 20, latitude, longitude, 22, get_date(5), 35, 29, False)
        Database.record_position(None, car.vin, 30, latitude, longitude, 22, end, 30, 28, False)
        trips = Trips.get_trips(self.vehicule_list)
        res = trips[car.vin].get_trips_as_dict()
        print(res)
        assert compare_dict(res, [{'consumption_km': 6.947368421052632,
                                   'start_at': start,
                                   'consumption_by_temp': None,
                                   'positions': {'lat': [latitude],
                                                'long': [longitude]},
                                   'duration': 120.0,
                                   'speed_average': 9.5,
                                   'distance': 19.0,
                                   'mileage': 30.0,
                                   'altitude_diff': 0,
                                   'id': 1,
                                   'consumption': 1.32,
                                   'consumption_fuel_km': 10.53}])

    def test_db_callback(self):
        old_dummy_value = dummy_value
        get_new_test_db()
        Database.set_db_callback(callback_test)
        assert old_dummy_value == dummy_value
        Database.record_position(None, "xx", 11, latitude, longitude - 0.05, None, date0, 40, None, False)
        assert old_dummy_value != dummy_value

    def test_parse_hour(self):
        expected_res = [[2, 0, 0], [3, 14, 0], [0, 0, 2], [0, 30, 0]]
        assert expected_res == [parse_hour(h) for h in ["PT2H", "PT3H14", "PT2S", "PT30M"]]

    def test_rate_limit(self):
        @rate_limit(2, 10)
        def test_fct():
            pass
        test_fct()
        test_fct()
        try:
            test_fct()
            raise Exception("It should have raise RateLimitException")
        except RateLimitException:
            pass


if __name__ == '__main__':
    my_logger(handler_level=os.environ.get("DEBUG_LEVEL", 20))
    unittest.main()
