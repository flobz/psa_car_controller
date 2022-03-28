# flake8: noqa
import json
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import reverse_geocode
from dateutil.tz import tzutc
from greenery.lego import parse, charclass
from pytz import UTC

from psa_car_controller import psa
from psa_car_controller.common import utils
from psa_car_controller.common.mylogger import my_logger

from psa_car_controller.common.utils import parse_hour, RateLimitException, rate_limit
from psa_car_controller.psa.otp.otp import load_otp, save_otp
from psa_car_controller.psa.setup.app_decoder import get_content_from_apk, GITHUB_USER, GITHUB_REPO
from psa_car_controller.psa.setup.github import github_file_need_to_be_downloaded
from psa_car_controller.psa.connected_car_api import ApiClient
from psa_car_controller.psacc.application.charge_control import ChargeControls
from psa_car_controller.psacc.application.charging import Charging
from psa_car_controller.psacc.application.ecomix import Ecomix
from psa_car_controller.psacc.application.psa_client import PSAClient
from psa_car_controller.psacc.model.car import Car, Cars
from psa_car_controller.psacc.repository import config_repository
from psa_car_controller.psacc.repository.car_model import CarModelRepository
from psa_car_controller.psacc.repository.config_repository import ConfigRepository
from psa_car_controller.psacc.repository.db import Database
from psa_car_controller.psacc.repository.trips import Trips
from psa_car_controller.psacc.utils.utils import get_temp
from tests.data.car_status import FUEL_CAR_STATUS, ELECTRIC_CAR_STATUS
from tests.utils import DATA_DIR, record_position, latitude, longitude, date0, date1, date2, date3, record_charging, \
    vehicule_list, get_new_test_db, get_date, date4
from psa_car_controller.web.figures import get_figures, get_battery_curve_fig, get_altitude_fig
from deepdiff import DeepDiff


def compare_dict(result, expected):
    diff = DeepDiff(expected, result)
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
            myp = PSAClient.load_config("config.json")
            myp.refresh_token()
            myp.get_vehicles()
            car = myp.vehicles_list[0]
            myp.abrp.abrp_enable_vin.add(car.vin)
            myp.get_vehicle_info(myp.vehicles_list[0].vin)
            myp.abrp.call(car, 22.1)
            assert isinstance(get_temp(str(latitude), str(longitude), myp.weather_api), float)

    def test_car_model(self):
        assert CarModelRepository().find_model_by_vin("VR3UHZKXZL").name == "e-208"
        assert CarModelRepository().find_model_by_vin("VR3UKZKXZM").name == "e-2008"
        assert CarModelRepository().find_model_by_vin("VXKUHZKXZL").name == "corsa-e"

    def test_c02_signal_cache(self):
        start = datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=30)
        end = datetime.utcnow().replace(tzinfo=UTC)
        Ecomix._cache = {'FR': [[start - timedelta(days=1), 100],
                                [start + timedelta(minutes=1), 10],
                                [start + timedelta(minutes=2), 20],
                                [start + timedelta(minutes=3), 30]]}
        assert Ecomix.get_co2_from_signal_cache(start, end, "FR") == 20
        Ecomix.clean_cache()
        self.assertEqual(3, len(Ecomix._cache["FR"]))

    def test_c02_signal(self):
        if self.test_online:
            key = "d186c74bfbcd1da8"
            Ecomix.co2_signal_key = key
            def_country = "FR"
            Ecomix.get_data_from_co2_signal(latitude, longitude, def_country)
            res = Ecomix.get_co2_from_signal_cache(datetime.utcnow().replace(tzinfo=UTC) - timedelta(minutes=5),
                                                   datetime.now(), def_country)
            assert isinstance(res, float)

    def test_charge_control(self):
        charge_control = ChargeControls()
        charge_control.file_name = "test_charge_control.json"
        charge_control.save_config(force=True)

    def test_battery_curve(self):
        vin = self.vehicule_list[0].vin
        get_new_test_db()
        record_charging()
        charge = Database.get_last_charge(vin)
        self.assertEqual(charge.stop_at, date4)
        res = Database.get_battery_curve(Database.get_db(), date0, date4, vin)
        self.assertEqual(4, len(res))

    def test_set_charge_price(self):
        vin = self.vehicule_list[0].vin
        get_new_test_db()
        record_charging()
        charge = Database.get_last_charge(vin)
        charge.price = 42
        conn = Database.get_db()
        Database.set_chargings_price(conn, charge)
        conn.close()
        res = Database.get_charge(vin, charge.start_at)
        self.assertEqual(charge.price, res.price)

    def test_sdk(self):
        api = ApiClient()
        status: psa.connected_car_api.models.status.Status = api._ApiClient__deserialize(FUEL_CAR_STATUS, "Status")
        geocode_res = reverse_geocode.search([(status.last_position.geometry.coordinates[:2])[::-1]])[0]
        get_new_test_db()
        car = Car("XX", "vid", "Peugeot")
        car.status = status
        myp = PSAClient.load_config(DATA_DIR + "config.json")
        myp.record_info(car)
        assert geocode_res["country_code"] == "DE"
        assert "features" in json.loads(Database.get_recorded_position())
        # electric should be first
        assert car.status.energy[0].type == 'Electric'

    @patch("psa_car_controller.psacc.repository.db.Database.record_position")
    def test_electric_record_info(self, mock_db):
        api = ApiClient()
        status: psa.connected_car_api.models.status.Status = api._ApiClient__deserialize(ELECTRIC_CAR_STATUS, "Status")
        get_new_test_db()
        car = self.vehicule_list[0]
        car.status = status
        myp = PSAClient.load_config(DATA_DIR + "config.json")
        myp.record_info(car)
        db_record_position_arg = mock_db.call_args_list[0][0]
        expected_result = (None, 'VR3UHZKX', 3196.5, 47.274, -1.59008, 30,
                           datetime(2022, 3, 26, 11, 2, 54, tzinfo=tzutc()),
                           59.0,
                           None,
                           True)
        self.assertEqual(db_record_position_arg, expected_result)

    def test_record_position_charging(self):
        get_new_test_db()
        config_repository.CONFIG_FILENAME = DATA_DIR + "config.ini"
        car = self.vehicule_list[0]
        record_position()
        utils.get_positions = MagicMock(
            return_value=[{'dataset': 'srtm30m', 'elevation': 40.0, 'location': {'lat': 47.2183, 'lng': -1.60362}}])
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

        Charging.elec_price = ConfigRepository.read_config(DATA_DIR + "config.ini").Electricity_config
        start_level = 40
        end_level = 85
        Charging.record_charging(car, "InProgress", date0, start_level, latitude, longitude, None, "slow", 20, 60)
        Charging.record_charging(car, "InProgress", date1, 70, latitude, longitude, "FR", "slow", 20, 60)
        Charging.record_charging(car, "InProgress", date1, 70, latitude, longitude, "FR", "slow", 20, 60)
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
        assert get_figures(car)
        row = {"start_at": date0.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
               "stop_at": date3.strftime('%Y-%m-%dT%H:%M:%S.000Z'), "start_level": start_level, "end_level": end_level}
        battery_curve_fix = get_battery_curve_fig(row, car)
        assert battery_curve_fix is not None
        assert get_altitude_fig(trip) is not None

    def test_fuel_car(self):
        get_new_test_db()
        config_repository.CONFIG_FILENAME = DATA_DIR + "config.ini"
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
                                   'consumption_fuel_km': 4.53}])

    def test_none_mileage(self):
        get_new_test_db()
        config_repository.CONFIG_FILENAME = DATA_DIR + "config.ini"
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
                                   'consumption_fuel_km': 4.53}])

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

    def test_parse_apk(self):
        filename = "mypeugeot.apk"
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        assert get_content_from_apk(filename, "FR")
        assert github_file_need_to_be_downloaded(GITHUB_USER, GITHUB_REPO, "", filename) is False

    def test_file_need_to_be_updated(self):
        filename = "mypeugeot.apk"
        with open(filename, "w") as f:
            f.write(" ")
        assert github_file_need_to_be_downloaded(GITHUB_USER, GITHUB_REPO, "", filename) is True

    def test_regex(self):
        car_models = CarModelRepository().models
        for x in range(0, len(car_models)):
            for y in range(x + 1, len(car_models)):
                reg_a = car_models[x].reg
                reg_b = car_models[y].reg
                res: charclass = parse(reg_a) & parse(reg_b)
                self.assertTrue(res.empty(), msg=f"{reg_a} and {reg_b} can match the same string")


if __name__ == '__main__':
    my_logger(handler_level=os.environ.get("DEBUG_LEVEL", 20))
    unittest.main()
