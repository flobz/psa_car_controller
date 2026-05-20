import json
import os
import unittest
from configparser import ConfigParser
from unittest.mock import patch

from psa_car_controller.common.mylogger import my_logger

from psa_car_controller.psacc.repository.config_repository import ConfigRepository


class TestUnit(unittest.TestCase):
    def test_read_config(self):
        from psa_car_controller.psacc.repository.config_repository import ConfigRepository
        ConfigRepository.read_config()

    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._write")
    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._read_file")
    def test_read_old_config(self, mock_read, mock_write):
        old_config_str = """[General]
currency = €

[Electricity config]
day price = 42
night price = 0.1
night hour start = 1h00
night hour end = 4h42

"""
        mock_read.return_value = old_config_str
        conf = ConfigRepository.read_config()
        conf.write_config(conf)
        config_written: ConfigParser = mock_write.call_args_list[0][0][1]
        self.assertEqual(config_written["General"]["currency"].value, "€")
        self.assertEqual(config_written["Electricity config"]["day price"].value, 42)
        self.assertEqual(config_written["Electricity config"]["night price"].value, 0.1)
        self.assertEqual(str(config_written["Electricity config"]["night hour start"].value), "1h00")
        self.assertEqual(str(config_written["Electricity config"]["night hour end"].value), "4h42")
        conf.json()

    def test_read_non_existent_config(self):
        from psa_car_controller.psacc.repository.config_repository import ConfigRepository
        self.assertRaises(FileNotFoundError, lambda: ConfigRepository._read_file("nonexistent.ini"))

    def test_read_config_non_existent_config(self):
        from psa_car_controller.psacc.repository.config_repository import ConfigRepository
        result = ConfigRepository.read_config("nonexistent.ini")
        expected_result = ConfigRepository.config_file_to_dto(ConfigRepository.get_default_config())
        self.assertEqual(result, expected_result)

    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._write")
    def test_read_invalid_hour(self, mock_write):
        conf = ConfigRepository.config_file_to_dto(ConfigRepository.get_default_config())
        conf.Electricity_config.night_hour_start = "200"
        self.assertRaises(ValueError, lambda: conf.write_config())

    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._write")
    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._read_file")
    def test_options_use_imperial_default_false(self, mock_read, mock_write):
        """Options.use_imperial should default to False when the section is absent."""
        old_config_str = """[General]
currency = €

[Electricity config]
day price = 0.15

"""
        mock_read.return_value = old_config_str
        conf = ConfigRepository.read_config()
        self.assertFalse(conf.Options.use_imperial)

    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._write")
    @patch("psa_car_controller.psacc.repository.config_repository.ConfigRepository._read_file")
    def test_options_use_imperial_persists(self, mock_read, mock_write):
        """Setting use_imperial = true in the ini should be read back as True."""
        config_str = """[General]
currency = €

[Options]
use imperial = true

[Electricity config]
day price = 0.15

"""
        mock_read.return_value = config_str
        conf = ConfigRepository.read_config()
        self.assertTrue(conf.Options.use_imperial)

    def test_convert_trips_for_display_metric(self):
        """When USE_IMPERIAL is False, convert_trips_for_display should return data unchanged."""
        from psa_car_controller.web import figures
        figures.USE_IMPERIAL = False
        trip = {"distance": 100.0, "mileage": 5000.0, "speed_average": 80.0,
                "consumption_km": 20.0, "consumption_fuel_km": 6.0}
        result = figures.convert_trips_for_display([trip])
        self.assertEqual(result, [trip])

    def test_convert_trips_for_display_imperial(self):
        """When USE_IMPERIAL is True, convert_trips_for_display should convert distance/speed fields."""
        from psa_car_controller.web import figures
        figures.USE_IMPERIAL = True
        trip = {"distance": 100.0, "mileage": 5000.0, "speed_average": 100.0,
                "consumption_km": 20.0, "consumption_fuel_km": 6.0}
        result = figures.convert_trips_for_display([trip])
        self.assertAlmostEqual(result[0]["distance"], 62.1371, places=3)
        self.assertAlmostEqual(result[0]["mileage"], 3106.855, places=2)
        self.assertAlmostEqual(result[0]["speed_average"], 62.1371, places=3)
        # restore
        figures.USE_IMPERIAL = False


if __name__ == '__main__':
    my_logger(handler_level=os.environ.get("DEBUG_LEVEL", 20))
    unittest.main()
