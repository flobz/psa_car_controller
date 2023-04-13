import logging
import unittest
import datetime
from time import sleep

from psa_car_controller.common.mylogger import my_logger
from psa_car_controller.psa.constants import INPROGRESS, STOPPED
from psa_car_controller.psacc.application.charge_control import ChargeControl

# This simulates a 70 % charge limit with the scheduled charge time set to currentTime + 2 minutes. The initial fake
# status is "75 % and charging InProgress". First, ChargeControl should stop the charge.
#
# The fake status then changes to "75 % and charging Stopped, but still plugged". Since the scheduled charge time is
# only 2 minutes away, ChargeControl postpones the charge to the next day. It does so by setting the scheduled charge
# time to (currentHour - 1):00. For instance, when it's 14:21, it will change the scheduled charge time to 13:00,
# which has to be on the next day.
#
# For reference, here is a correct sample output:
# 2022-04-20 12:31:15,551 :: INFO :: charging status of 123 is InProgress, battery level: 75
# 2022-04-20 12:31:15,552 :: INFO :: Charge threshold is reached, stop the charge
# 2022-04-20 12:31:15,552 :: INFO :: charge_now(123, False)
# 2022-04-20 12:31:15,552 :: INFO :: Approaching scheduled charging time, but should not charge. Postponing charge hour!
# 2022-04-20 12:31:15,552 :: INFO :: Changing stop_hour to 11:0


class TestChargeControl(unittest.TestCase):

    def test_charge_control(self):
        my_logger()
        ChargeControl.MQTT_TIMEOUT = 0

        now = datetime.datetime.now()
        stop_hour = now + datetime.timedelta(minutes=2)

        vin = "123"
        percentage_threshold = 70

        state = {
            "charging": True,
            "stop_hour": [stop_hour.hour, stop_hour.minute]
        }

        expectations = {
            "stopped_charge": False,
            "postponed_charge": False
        }

        def met_expectations():
            return expectations["stopped_charge"] and expectations["postponed_charge"]

        class MockClient:
            def charge_now(self, vin, now):
                logging.getLogger().info(f"charge_now({vin}, {now})")
                state["charging"] = now
                if not now:
                    expectations["stopped_charge"] = True

            def get_charge_hour(self, vin):
                return state["stop_hour"]

            def change_charge_hour(self, vin, hour, minute):
                logging.getLogger().info(f"Changing stop_hour to {hour}:{minute}")
                state["stop_hour"] = [hour, minute]
                expectations["postponed_charge"] = True

        mock_client = MockClient()

        class MockCharging:
            def __init__(self):
                self.status = INPROGRESS if state["charging"] else STOPPED
                self.charging_mode = "slow"

        class MockEnergy:
            def __init__(self):
                self.charging = MockCharging()
                self.level = 75
                self.updated_at = datetime.datetime.now(datetime.timezone.utc)

        class MockStatus:
            def get_energy(self, energy_type):
                return MockEnergy()

        class MockCar:
            def get_status(self):
                return MockStatus()

            def get_energy(self):
                return MockEnergy()

        class MockVehiclesList:
            def get_car_by_vin(self, vin):
                return MockCar()

        mock_vehicles_list = MockVehiclesList()

        class MockPsa:
            def __init__(self):
                self.vehicles_list = mock_vehicles_list
                self.remote_client = mock_client
                self.info_refresh_rate = 1

            def get_vehicle_info(self, vin):
                return MockStatus()

        mock_psac = MockPsa()
        # noinspection PyTypeChecker
        cc = ChargeControl(mock_psac, vin, percentage_threshold, state["stop_hour"])

        rounds = 0
        while not met_expectations() and rounds < 10:
            cc.process()
            rounds += 1
        self.assertTrue(expectations["stopped_charge"], "charge_now(..., False) should be called to stop the charge")
        self.assertTrue(expectations["postponed_charge"], "change_charge_hour(...) should be called to postpone "
                                                          "the charge until the next day")


if __name__ == '__main__':
    unittest.main()
