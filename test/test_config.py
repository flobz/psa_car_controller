import os
import unittest
from configparser import ConfigParser
from unittest.mock import MagicMock

from configupdater import ConfigUpdater

from common.mylogger import my_logger
from psacc.repository.config_repository import ConfigRepository


class TestUnit(unittest.TestCase):
    def test_read_config(self):
        config = ConfigRepository.read_config()

    def test_read_old_config(self):
        old_config = ConfigUpdater()
        old_config_str = """[General]
currency = €

[Electricity config]
day price = 42
night price = 0.1
night hour start = 1h00 
night hour end = 4h42

"""
        ConfigRepository._read_file = MagicMock(return_value=old_config_str)
        ConfigRepository._write = MagicMock()
        conf = ConfigRepository.read_config()
        conf.write_config(conf)
        config_written: ConfigParser = ConfigRepository._write.call_args_list[0][0][1]
        self.assertEqual(config_written["General"]["currency"].value, "€")
        self.assertEqual(config_written["Electricity config"]["day price"].value, 42)
        print(config_written)

    def test_read_non_existent_config(self):
        self.assertRaises(FileNotFoundError, lambda :ConfigRepository._read_file("nonexistent.ini"))

    def test_read_config_non_existent_config(self):
        result = ConfigRepository.read_config("nonexistent.ini")
        expected_result = ConfigRepository.config_file_to_dto(ConfigRepository.get_default_config())
        self.assertEqual(result,expected_result)

if __name__ == '__main__':
    my_logger(handler_level=os.environ.get("DEBUG_LEVEL", 20))
    unittest.main()
