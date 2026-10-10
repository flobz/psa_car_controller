import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from psa_car_controller.psa.RemoteClient import MQTT_EVENT_TOPIC

from tests.utils import get_rc

VIN = "VR3UHZKX"


class FakeTimer:
    created = []

    def __init__(self, interval, function, args=None, kwargs=None):
        self.interval = interval
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.daemon = False
        self.started = False
        self.cancelled = False
        FakeTimer.created.append(self)

    def start(self):
        self.started = True

    def cancel(self):
        self.cancelled = True

    def join(self, timeout=None):
        pass

    def fire(self):
        if not self.cancelled:
            self.function(*self.args, **self.kwargs)


def event(charging_state):
    payload = {"vin": VIN, "charging_state": charging_state, "precond_state": {}}
    return SimpleNamespace(topic=MQTT_EVENT_TOPIC + VIN, payload=json.dumps(payload).encode())


class TestFixNotUpdatedApi(unittest.TestCase):

    def setUp(self):
        FakeTimer.created = []
        self.charging = SimpleNamespace(status="Disconnected")
        car = MagicMock()
        car.status.get_energy.return_value = SimpleNamespace(charging=self.charging)
        self.rc = get_rc()
        self.rc.vehicles_list = MagicMock()
        self.rc.vehicles_list.get_car_by_vin.return_value = car
        self.wakeup = MagicMock()
        self.rc.wakeup = self.wakeup
        timer_patcher = patch("psa_car_controller.psa.RemoteClient.threading.Timer", FakeTimer)
        timer_patcher.start()
        self.addCleanup(timer_patcher.stop)
        sleep_patcher = patch("time.sleep")
        self.sleep = sleep_patcher.start()
        self.addCleanup(sleep_patcher.stop)

    def test_mqtt_callback_does_not_block(self):
        # GIVEN a charging event while the api doesn't report the charge yet
        # WHEN the mqtt callback handles it
        self.rc._on_mqtt_message(None, None, event({"rate": 4, "remaining_time": 120}))

        # THEN the paho network thread isn't blocked: the delayed wakeup is scheduled on a timer
        self.sleep.assert_not_called()
        self.wakeup.assert_not_called()
        self.assertEqual(1, len(FakeTimer.created))
        self.assertEqual(60, FakeTimer.created[0].interval)
        self.assertTrue(FakeTimer.created[0].daemon)
        self.assertTrue(FakeTimer.created[0].started)

        FakeTimer.created[0].fire()
        self.wakeup.assert_called_once_with(VIN)

    def test_repeated_events_schedule_one_wakeup_per_vin(self):
        for _ in range(5):
            self.rc._on_mqtt_message(None, None, event({"rate": 4}))
        self.assertEqual(1, len(FakeTimer.created))

        FakeTimer.created[0].fire()
        self.wakeup.assert_called_once_with(VIN)

        # a new event after the delayed check can schedule again
        self.rc._on_mqtt_message(None, None, event({"rate": 4}))
        self.assertEqual(2, len(FakeTimer.created))

    def test_no_wakeup_if_api_caught_up(self):
        self.rc._on_mqtt_message(None, None, event({"rate": 4}))
        self.charging.status = "InProgress"

        FakeTimer.created[0].fire()

        self.wakeup.assert_not_called()

    def test_stop_cancels_pending_wakeup(self):
        self.rc._on_mqtt_message(None, None, event({"rate": 4}))
        timer = FakeTimer.created[0]

        self.rc.stop()
        timer.fire()
        # a worker which was already running when stop() was called must not wake the car either
        self.rc._delayed_api_update(VIN)

        self.assertTrue(timer.cancelled)
        self.wakeup.assert_not_called()
        self.rc._on_mqtt_message(None, None, event({"rate": 4}))
        self.assertEqual(1, len(FakeTimer.created))


if __name__ == '__main__':
    unittest.main()
