import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

from psa_car_controller.psacc.application.car_controller import PSACarController

VIN = "VR3UHZKX00000001"


def new_psa_client():
    psacc = MagicMock()
    psacc.info_callback = []
    psacc.remote_client.mqtt_client = None
    return psacc


class TestStartRemoteControl(unittest.TestCase):
    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.charge_config = os.path.join(tmp_dir.name, "charge_config.json")
        # skip the singleton and __init__: they parse the command line and read config.ini
        self.app = PSACarController.__new__(PSACarController)
        self.app.args = SimpleNamespace(remote_disable=False, web_conf=False, charge_control=self.charge_config)
        self.app.chc = None
        self.app.myp = new_psa_client()

    def write_charge_config(self, percentage_threshold):
        with open(self.charge_config, "w", encoding="utf-8") as f:
            json.dump({VIN: {"percentage_threshold": percentage_threshold, "stop_hour": [9, 0]}}, f)

    def test_restart_keeps_one_charge_control_per_car(self):
        # start, then OTP config: start_remote_control runs again with the same PSA client
        self.write_charge_config(80)
        self.app.start_remote_control()
        self.write_charge_config(70)
        self.app.start_remote_control()
        self.assertEqual([self.app.chc.get(VIN).process], self.app.myp.info_callback)
        self.assertEqual(70, self.app.chc.get(VIN).percentage_threshold)

    def test_login_stops_charge_control_of_previous_client(self):
        # login: load_app replaces the PSA client before start_remote_control runs again
        self.write_charge_config(80)
        self.app.start_remote_control()
        previous_client = self.app.myp
        self.app.myp = new_psa_client()
        self.app.start_remote_control()
        self.assertEqual([], previous_client.info_callback)
        self.assertEqual([self.app.chc.get(VIN).process], self.app.myp.info_callback)

    def test_unreadable_config_keeps_running_charge_control(self):
        self.write_charge_config(80)
        self.app.start_remote_control()
        running = self.app.chc
        with open(self.charge_config, "w", encoding="utf-8") as f:
            f.write("{not json")
        with self.assertRaises(ValueError):
            self.app.start_remote_control()
        self.assertIs(running, self.app.chc)
        self.assertEqual([running.get(VIN).process], self.app.myp.info_callback)


if __name__ == '__main__':
    unittest.main()
