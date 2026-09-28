import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from psa_car_controller.psa.RemoteClient import MAX_REFRESH_DELAY, RemoteClient
from psa_car_controller.psa.RemoteCredentials import RemoteCredentials

from tests.utils import get_rc


def get_remote_client(remote_refresh_token="remote_refresh_token"):
    remote_client: RemoteClient = get_rc()
    remote_client.manager = MagicMock()
    remote_client.manager.refresh_token_now.return_value = True
    res = MagicMock()
    res.json.return_value = {"access_token": "access_token"}
    remote_client.manager.post.return_value = res
    remote_client.remoteCredentials = RemoteCredentials(remote_refresh_token)
    remote_client.mqtt_client = MagicMock()
    return remote_client


class TestRefreshRemoteToken(unittest.TestCase):

    def test_forced_refresh_is_throttled(self):
        # GIVEN a remote client whose token was just refreshed
        remote_client = get_remote_client()
        remote_client.remote_token_last_update = datetime.now()

        # WHEN a forced refresh is requested (e.g. on mqtt disconnect rc 7)
        refreshed = remote_client._refresh_remote_token(force=True)

        # THEN the refresh is skipped: it happened less than MAX_REFRESH_DELAY ago
        self.assertTrue(refreshed)
        remote_client.manager.refresh_token_now.assert_not_called()
        remote_client.manager.post.assert_not_called()

    def test_forced_refresh_after_max_delay(self):
        # GIVEN a remote client whose token was refreshed MAX_REFRESH_DELAY ago
        remote_client = get_remote_client()
        remote_client.remote_token_last_update = datetime.now() - timedelta(seconds=MAX_REFRESH_DELAY)

        # WHEN a forced refresh is requested
        refreshed = remote_client._refresh_remote_token(force=True)

        # THEN the token is actually refreshed
        self.assertTrue(refreshed)
        remote_client.manager.refresh_token_now.assert_called_once()
        remote_client.manager.post.assert_called_once()
        self.assertEqual("access_token", remote_client.remoteCredentials.access_token)
        self.assertIsNotNone(remote_client.remote_token_last_update)

    def test_first_forced_refresh_is_not_throttled(self):
        # GIVEN a remote client which never refreshed its token
        remote_client = get_remote_client()
        self.assertIsNone(remote_client.remote_token_last_update)

        # WHEN a forced refresh is requested
        refreshed = remote_client._refresh_remote_token(force=True)

        # THEN the token is refreshed
        self.assertTrue(refreshed)
        remote_client.manager.refresh_token_now.assert_called_once()

    def test_unforced_refresh_respects_ttl(self):
        # GIVEN a remote client whose remote credentials were updated less than MQTT_TOKEN_TTL ago
        remote_client = get_remote_client()
        remote_client.remoteCredentials.refresh_token = "new_remote_refresh_token"

        # WHEN a refresh is requested without force
        refreshed = remote_client._refresh_remote_token()

        # THEN no refresh is performed
        self.assertTrue(refreshed)
        remote_client.manager.refresh_token_now.assert_not_called()


if __name__ == '__main__':
    unittest.main()
