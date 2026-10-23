import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from psa_car_controller.psa.setup.app_decoder import InitialSetup
from psa_car_controller.psacc.application.charge_control import ChargeControls

VIN1 = "VR3UHZKX00000001"
VIN2 = "VR3UHZKX00000002"
OLD_VIN = "VR3UHZKX00000003"
DEFAULT = {"percentage_threshold": 100, "stop_hour": None}


class TestInitialSetupChargeControl(unittest.TestCase):
    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.prefix = tmp_dir.name + os.sep
        self.charge_config = self.prefix + "charge_config.json"

    def write_charge_config(self, content):
        with open(self.charge_config, "w", encoding="utf-8") as f:
            f.write(content if isinstance(content, str) else json.dumps(content))

    def read_charge_config(self):
        with open(self.charge_config, "r", encoding="utf-8") as f:
            return json.load(f)

    def connect(self, *vins):
        # skip __init__: it logs in to PSA servers
        setup = InitialSetup.__new__(InitialSetup)
        setup.user_info = {"vehicles": []}
        setup.psacc = MagicMock()
        setup.psacc.get_vehicles.return_value = [MagicMock(vin=vin) for vin in vins]
        with patch("psa_car_controller.psa.setup.app_decoder.PSACarController"):
            setup.connect("code", config_prefix=self.prefix)
        return self.read_charge_config()

    def test_first_login_disables_charge_control(self):
        self.assertEqual({VIN1: DEFAULT}, self.connect(VIN1))

    def test_login_keeps_charge_settings(self):
        settings = {VIN1: {"percentage_threshold": 80, "stop_hour": [9, 0]}}
        self.write_charge_config(settings)
        self.assertEqual(settings, self.connect(VIN1))

    def test_login_adds_new_car_and_drops_removed_car(self):
        self.write_charge_config({VIN1: {"percentage_threshold": 80, "stop_hour": [9, 0]},
                                  OLD_VIN: {"percentage_threshold": 70, "stop_hour": None}})
        self.assertEqual({VIN1: {"percentage_threshold": 80, "stop_hour": [9, 0]}, VIN2: DEFAULT},
                         self.connect(VIN1, VIN2))

    def test_login_fills_missing_fields(self):
        self.write_charge_config({VIN1: {"percentage_threshold": 80}, VIN2: "invalid"})
        self.assertEqual({VIN1: {"percentage_threshold": 80, "stop_hour": None}, VIN2: DEFAULT},
                         self.connect(VIN1, VIN2))

    def test_login_keeps_disabled_stop_hour(self):
        self.write_charge_config({VIN1: {"percentage_threshold": 80, "stop_hour": [0, 0]}})
        self.assertEqual({VIN1: {"percentage_threshold": 80, "stop_hour": None}}, self.connect(VIN1))

    def test_login_resets_invalid_settings(self):
        for settings in ({"percentage_threshold": 80, "stop_hour": [25, 0]},
                         {"percentage_threshold": 80, "stop_hour": [9]},
                         {"percentage_threshold": 80, "stop_hour": "09:00"},
                         {"percentage_threshold": None, "stop_hour": [9, 0]}):
            with self.subTest(settings=settings):
                self.write_charge_config({VIN1: settings})
                with self.assertLogs("psa_car_controller.psa.setup.app_decoder", level="WARNING"):
                    self.assertEqual({VIN1: DEFAULT}, self.connect(VIN1))

    def test_login_resets_unreadable_charge_config(self):
        for content in ("{not json", "[]"):
            with self.subTest(content=content):
                self.write_charge_config(content)
                with self.assertLogs("psa_car_controller.psa.setup.app_decoder", level="WARNING"):
                    self.assertEqual({VIN1: DEFAULT}, self.connect(VIN1))

    def test_kept_settings_are_loaded_by_charge_control(self):
        self.write_charge_config({VIN1: {"percentage_threshold": 80, "stop_hour": [9, 0]}})
        self.connect(VIN1)
        charge_control = ChargeControls.load_config(MagicMock(), name=self.charge_config).get(VIN1)
        self.assertEqual(80, charge_control.percentage_threshold)
        self.assertEqual([9, 0], charge_control.get_stop_hour())


if __name__ == '__main__':
    unittest.main()
