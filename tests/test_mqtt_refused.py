import time
import unittest
from unittest import mock
from unittest.mock import MagicMock

from psa_car_controller.psa.RemoteClient import MQTT_REBUILD_DELAY, RemoteClient

from tests.test_refresh_remote_token import get_remote_client


class TestMqttRefused(unittest.TestCase):
    """The broker refusing the sign-in (CONNACK 5) on every reconnect."""

    def setUp(self):
        self.remote_client = get_remote_client()
        self.remote_client._refresh_remote_token = MagicMock(return_value=True)
        self.remote_client.vehicles_list = []
        self.rebuild = mock.patch.object(RemoteClient, "_rebuild_mqtt").start()
        # run the rebuild thread's target at once
        self.thread = mock.patch("psa_car_controller.psa.RemoteClient.threading.Thread",
                                 side_effect=lambda target, daemon: MagicMock(start=target)).start()
        self.addCleanup(mock.patch.stopall)

    def disconnect(self, code=5):
        self.remote_client._on_mqtt_disconnect(None, None, code)

    def test_first_refusal_refreshes_the_token(self):
        self.disconnect()
        self.remote_client._refresh_remote_token.assert_called_once_with(force=True)
        self.rebuild.assert_not_called()

    def test_refusal_after_a_refresh_rebuilds_the_client(self):
        self.disconnect()
        self.disconnect(4)
        self.rebuild.assert_called_once()

    def test_rebuilds_are_throttled(self):
        for _ in range(6):
            self.disconnect()
        self.rebuild.assert_called_once()

    def test_rebuilds_again_after_the_delay(self):
        self.disconnect()
        self.disconnect()
        self.remote_client.mqtt_rebuilt_at = time.time() - MQTT_REBUILD_DELAY
        self.disconnect()
        self.disconnect()
        self.assertEqual(2, self.rebuild.call_count)

    def test_a_successful_sign_in_resets_the_count(self):
        self.disconnect()
        self.remote_client._RemoteClient__on_mqtt_connect(MagicMock(), None, {}, 0)
        self.disconnect()
        self.assertEqual(2, self.remote_client._refresh_remote_token.call_count)
        self.rebuild.assert_not_called()

    def test_a_refused_sign_in_does_not_subscribe(self):
        client = MagicMock()
        self.remote_client._RemoteClient__on_mqtt_connect(client, None, {}, 5)
        client.subscribe.assert_not_called()

    def test_other_disconnects_are_left_alone(self):
        self.disconnect(16)
        self.remote_client._refresh_remote_token.assert_not_called()
        self.rebuild.assert_not_called()

    def test_rebuild_stops_and_starts(self):
        mock.patch.stopall()
        self.remote_client.stop = MagicMock()
        self.remote_client.start = MagicMock()
        self.remote_client._rebuild_mqtt()
        self.remote_client.stop.assert_called_once()
        self.remote_client.start.assert_called_once()

    def test_a_new_client_soon_after_a_refresh_is_signed_in(self):
        mock.patch.stopall()
        remote_client = get_remote_client()
        remote_client.remoteCredentials.access_token = "access_token"
        remote_client.remoteCredentials.refresh_token = "new_remote_refresh_token"
        remote_client.load_otp = MagicMock(return_value=True)
        with mock.patch("psa_car_controller.psa.RemoteClient.mqtt.Client") as client_class, \
                mock.patch.object(RemoteClient, "_RemoteClient__keep_mqtt"):
            remote_client.start()
        client_class.return_value.username_pw_set.assert_called_once_with("IMA_OAUTH_ACCESS_TOKEN", "access_token")
        remote_client.manager.refresh_token_now.assert_not_called()


if __name__ == '__main__':
    unittest.main()
