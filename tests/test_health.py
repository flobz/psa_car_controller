import unittest
from unittest.mock import MagicMock, patch

import paho.mqtt.client as mqtt

from psa_car_controller.psa.RemoteClient import RemoteClient
from psa_car_controller.psacc.application.health import get_health
from psa_car_controller.psacc.model.car import Cars

from tests.utils import get_rc

MAX_FAILURES = 5


def get_remote_client() -> RemoteClient:
    remote_client = get_rc()
    remote_client.vehicles_list = Cars()
    remote_client.mqtt_client = MagicMock()
    remote_client.mqtt_client.is_connected.return_value = False
    return remote_client


def refuse(remote_client: RemoteClient, times: int):
    for _ in range(times):
        remote_client._on_mqtt_disconnect(None, None, mqtt.MQTT_ERR_CONN_REFUSED)


def connect(remote_client: RemoteClient):
    remote_client.mqtt_client.is_connected.return_value = True
    remote_client._RemoteClient__on_mqtt_connect(MagicMock(), None, 0, None)


class TestMqttAuthFailureCounter(unittest.TestCase):

    def test_refused_disconnects_are_counted(self):
        remote_client = get_remote_client()
        refuse(remote_client, 3)
        self.assertEqual(3, remote_client.mqtt_auth_failures)

    def test_other_disconnects_are_not_counted(self):
        remote_client = get_remote_client()
        remote_client._on_mqtt_disconnect(None, None, mqtt.MQTT_ERR_PROTOCOL)
        self.assertEqual(0, remote_client.mqtt_auth_failures)

    def test_successful_connect_resets_the_counter(self):
        remote_client = get_remote_client()
        refuse(remote_client, 3)
        connect(remote_client)
        self.assertEqual(0, remote_client.mqtt_auth_failures)
        self.assertIsNotNone(remote_client.mqtt_last_connect)

    def test_refused_connack_does_not_reset_the_counter(self):
        # paho calls on_connect with the CONNACK code before on_disconnect when it is refused
        remote_client = get_remote_client()
        refuse(remote_client, 3)
        remote_client._RemoteClient__on_mqtt_connect(MagicMock(), None, 5, None)
        self.assertEqual(3, remote_client.mqtt_auth_failures)
        self.assertIsNone(remote_client.mqtt_last_connect)

    def test_stop_resets_the_counter(self):
        remote_client = get_remote_client()
        refuse(remote_client, 3)
        remote_client.stop()
        self.assertEqual(0, remote_client.mqtt_auth_failures)

    def test_start_resets_the_counter(self):
        remote_client = get_remote_client()
        refuse(remote_client, 3)
        with patch.object(remote_client, "load_otp", return_value=False):
            remote_client.start()
        self.assertEqual(0, remote_client.mqtt_auth_failures)


class TestHealth(unittest.TestCase):

    def test_healthy_while_connected(self):
        remote_client = get_remote_client()
        connect(remote_client)
        body, status = get_health(remote_client, True, MAX_FAILURES)
        self.assertEqual(200, status)
        self.assertTrue(body["mqtt_connected"])
        self.assertEqual(0, body["consecutive_auth_failures"])
        self.assertIsNotNone(body["last_connect"])

    def test_healthy_below_the_threshold(self):
        remote_client = get_remote_client()
        refuse(remote_client, MAX_FAILURES - 1)
        _, status = get_health(remote_client, True, MAX_FAILURES)
        self.assertEqual(200, status)

    def test_unhealthy_after_max_refusals(self):
        remote_client = get_remote_client()
        refuse(remote_client, MAX_FAILURES)
        body, status = get_health(remote_client, True, MAX_FAILURES)
        self.assertEqual(503, status)
        self.assertFalse(body["mqtt_connected"])
        self.assertEqual(MAX_FAILURES, body["consecutive_auth_failures"])
        self.assertIsNone(body["last_connect"])

    def test_one_connect_makes_it_healthy_again(self):
        remote_client = get_remote_client()
        refuse(remote_client, MAX_FAILURES)
        connect(remote_client)
        _, status = get_health(remote_client, True, MAX_FAILURES)
        self.assertEqual(200, status)

    def test_healthy_when_remote_control_is_disabled(self):
        remote_client = get_remote_client()
        refuse(remote_client, MAX_FAILURES)
        body, status = get_health(remote_client, False, MAX_FAILURES)
        self.assertEqual(200, status)
        self.assertEqual({"remote_control": False}, body)

    def test_healthy_without_client(self):
        _, status = get_health(None, True, MAX_FAILURES)
        self.assertEqual(200, status)


if __name__ == '__main__':
    unittest.main()
