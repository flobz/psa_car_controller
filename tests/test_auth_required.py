"""Regression tests for the "no access token" failure mode (Bearer + None).

When the refresh token is expired or revoked, PSAClient.manager.access_token is
None. Before this fix, PSAClient.api() handed that None straight to the
generated API client, which built an Authorization header with
``'Bearer ' + None`` and raised::

    TypeError: can only concatenate str (not "NoneType") to str

surfacing to callers as an HTTP 500 with a traceback that says nothing about
needing to reconnect.
"""
import os
import sys
from unittest import TestCase
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from psa_car_controller.common.utils import AuthenticationRequiredException  # noqa: E402
from psa_car_controller.psa.oauth import Oauth2PSACCApiConfig  # noqa: E402
from psa_car_controller.psacc.application.psa_client import PSAClient  # noqa: E402


class TestApiRequiresAccessToken(TestCase):
    @staticmethod
    def _client_with_token(token):
        client = PSAClient.__new__(PSAClient)  # bypass __init__, it does I/O
        client.manager = MagicMock()
        client.manager.access_token = token
        client.api_config = Oauth2PSACCApiConfig()  # real config: the API client reads attributes off it
        return client

    def test_missing_access_token_raises_authentication_required(self):
        for token in (None, ""):
            with self.subTest(token=token):
                client = self._client_with_token(token)
                with self.assertRaises(AuthenticationRequiredException):
                    client.api()

    def test_missing_access_token_does_not_raise_type_error(self):
        client = self._client_with_token(None)
        try:
            client.api()
        except AuthenticationRequiredException:
            pass
        except TypeError as e:  # pragma: no cover - the regression we fixed
            self.fail(f"api() still raises TypeError instead of a clear error: {e}")

    def test_access_token_is_passed_through_when_present(self):
        client = self._client_with_token("a-valid-token")
        client.api()
        self.assertEqual(client.api_config.access_token, "a-valid-token")


class TestAuthenticationRequiredException(TestCase):
    def test_default_message_tells_the_user_what_to_do(self):
        self.assertIn("reconnect", str(AuthenticationRequiredException()).lower())

    def test_custom_message_is_preserved(self):
        self.assertEqual(str(AuthenticationRequiredException("boom")), "boom")
