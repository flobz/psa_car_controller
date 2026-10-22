"""A refresh token PSA rejects (invalid_grant) needs a new login, not a refresh on every call.

Before, the expired access token stayed set, so every API call went to PSA, got a 401,
tried to refresh, failed again and answered 502 or, once the refresh was rate limited,
500 with a traceback, every two minutes until someone noticed.
"""
import time
import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from oauth2_client.credentials_manager import OAuthError, ServiceInformation
from requests import RequestException

from psa_car_controller.common.utils import AuthenticationRequiredException, RateLimitException
from psa_car_controller.psa.connected_car_api.rest import ApiException
from psa_car_controller.psa.oauth import (OpenIdCredentialManager, Oauth2PSACCApiConfig, OauthAPIClient,
                                          REJECTED_GRANT_RETRY_DELAY)
from psa_car_controller.psacc.application.psa_client import PSAClient


def invalid_grant():
    return OAuthError(HTTPStatus.BAD_REQUEST, "invalid_grant", "grant is invalid")


def get_manager() -> OpenIdCredentialManager:
    manager = OpenIdCredentialManager(ServiceInformation("https://idp.invalid/authorize",
                                                         "https://idp.invalid/token",
                                                         "client-id", "client-secret", ["openid"]))
    manager._access_token = "expired-access-token"
    return manager


def refresh(manager: OpenIdCredentialManager) -> bool:
    # bypass the rate limit: it is shared by every manager of the test run
    return OpenIdCredentialManager.refresh_token_now.__wrapped__(manager)


def reject(manager: OpenIdCredentialManager, seconds_ago: float = 0):
    manager.grant_rejected_at = time.monotonic() - seconds_ago


def get_client(manager: OpenIdCredentialManager) -> PSAClient:
    client = PSAClient.__new__(PSAClient)  # bypass __init__, it does I/O
    client.manager = manager
    client.api_config = Oauth2PSACCApiConfig()
    return client


class TestRejectedGrant(unittest.TestCase):

    def test_a_rejected_refresh_token_needs_a_login(self):
        manager = get_manager()
        with patch.object(manager, "_refresh_token", side_effect=invalid_grant()):
            self.assertFalse(refresh(manager))
        self.assertTrue(manager.needs_login)

    def test_an_unreachable_server_does_not_need_a_login(self):
        manager = get_manager()
        with patch.object(manager, "_refresh_token", side_effect=RequestException("down")), \
                patch("psa_car_controller.psa.oauth.time.sleep"):
            self.assertFalse(refresh(manager))
        self.assertFalse(manager.needs_login)

    def test_new_tokens_clear_it(self):
        manager = get_manager()
        reject(manager)
        manager._process_token_response({"access_token": "new", "refresh_token": "new"}, False)
        self.assertFalse(manager.needs_login)

    def test_retried_only_after_the_delay(self):
        manager = get_manager()
        self.assertFalse(manager.rejected_grant_retry_due())
        reject(manager)
        self.assertFalse(manager.rejected_grant_retry_due())
        reject(manager, REJECTED_GRANT_RETRY_DELAY + 1)
        self.assertTrue(manager.rejected_grant_retry_due())


class TestApiWithRejectedGrant(unittest.TestCase):

    def test_api_is_refused_without_calling_psa(self):
        manager = get_manager()
        reject(manager)
        client = get_client(manager)
        with patch.object(manager, "refresh_token_now") as refresh_token_now:
            with self.assertRaises(AuthenticationRequiredException):
                client.api()
        refresh_token_now.assert_not_called()
        self.assertFalse(client.is_authenticated())

    def test_api_works_again_when_the_retry_succeeds(self):
        manager = get_manager()
        reject(manager, REJECTED_GRANT_RETRY_DELAY + 1)
        client = get_client(manager)

        def accepted():
            manager.grant_rejected_at = None
            return True

        with patch.object(manager, "refresh_token_now", side_effect=accepted) as refresh_token_now:
            client.api()
        refresh_token_now.assert_called_once()
        self.assertTrue(client.is_authenticated())

    def test_api_is_refused_when_the_retry_is_rejected_again(self):
        manager = get_manager()
        reject(manager, REJECTED_GRANT_RETRY_DELAY + 1)
        client = get_client(manager)
        with patch.object(manager, "_refresh_token", side_effect=invalid_grant()), \
                patch.object(manager, "refresh_token_now", side_effect=lambda: refresh(manager)):
            with self.assertRaises(AuthenticationRequiredException):
                client.api()
        self.assertFalse(manager.rejected_grant_retry_due())

    def test_a_rate_limited_retry_is_not_an_error(self):
        manager = get_manager()
        reject(manager, REJECTED_GRANT_RETRY_DELAY + 1)
        client = get_client(manager)
        with patch.object(manager, "refresh_token_now", side_effect=RateLimitException("refresh_token_now")):
            with self.assertRaises(AuthenticationRequiredException):
                client.api()

    def test_vehicle_info_needs_a_login_after_the_refresh_is_rejected(self):
        manager = get_manager()
        client = get_client(manager)
        client.api_config.set_refresh_callback(lambda: refresh(manager))
        client.vehicles_list = MagicMock()
        unauthorized = ApiException(status=401, reason="Unauthorized")
        with patch.object(manager, "_refresh_token", side_effect=invalid_grant()), \
                patch.object(OauthAPIClient, "_ApiClient__call_api", side_effect=unauthorized) as call_api:
            with self.assertRaises(AuthenticationRequiredException):
                client.get_vehicle_info("VIN")
        # one call with the expired token, none after the refresh was rejected
        self.assertEqual(1, call_api.call_count)


class TestRateLimitedRefresh(unittest.TestCase):

    def test_the_caller_gets_the_401(self):
        config = Oauth2PSACCApiConfig()
        config.set_refresh_callback(MagicMock(side_effect=RateLimitException("refresh_token_now")))
        unauthorized = ApiException(status=401, reason="Unauthorized")
        with patch.object(OauthAPIClient, "_ApiClient__call_api", side_effect=unauthorized):
            with self.assertRaises(ApiException):
                OauthAPIClient(config).call_api("/user", "GET")


if __name__ == '__main__':
    unittest.main()
