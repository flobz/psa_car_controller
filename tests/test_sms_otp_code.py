import unittest
from unittest.mock import MagicMock

from requests import ConnectionError as RequestsConnectionError, ReadTimeout

from psa_car_controller.psa.RemoteClient import RemoteClient, RemoteException, SMS_TIMEOUT_IN_S, \
    SmsRequestException

from tests.utils import get_rc


def get_remote_client(status_code, text=""):
    remote_client: RemoteClient = get_rc()
    remote_client.manager = MagicMock()
    res = MagicMock()
    res.status_code = status_code
    res.ok = status_code < 400
    res.text = text
    remote_client.manager.post.return_value = res
    return remote_client


class TestSmsOtpCode(unittest.TestCase):

    def test_sms_request_accepted(self):
        # GIVEN PSA accepts the SMS request
        remote_client = get_remote_client(202)

        # WHEN an SMS code is requested
        res = remote_client.get_sms_otp_code()

        # THEN the response is returned without error
        self.assertEqual(202, res.status_code)

    def test_sms_request_rejected(self):
        # GIVEN PSA rejects the SMS request
        remote_client = get_remote_client(401, '{"error": "invalid_token"}')

        # WHEN an SMS code is requested
        # THEN an exception with status code and body is raised
        with self.assertRaises(RemoteException) as ctx:
            remote_client.get_sms_otp_code()
        self.assertIn("401", str(ctx.exception))
        self.assertIn("invalid_token", str(ctx.exception))
        self.assertIn("Reconnect", ctx.exception.hint)

    def test_sms_request_uses_the_longer_timeout(self):
        remote_client = get_remote_client(202)
        remote_client.get_sms_otp_code()
        self.assertEqual(SMS_TIMEOUT_IN_S, remote_client.manager.post.call_args.kwargs["timeout"])

    def test_sms_request_timeout_says_to_try_again(self):
        # GIVEN PSA doesn't answer in time
        remote_client = get_remote_client(202)
        remote_client.manager.post.side_effect = ReadTimeout("Read timed out.")

        # WHEN an SMS code is requested
        # THEN the user is told to try again rather than shown the raw error
        with self.assertRaises(SmsRequestException) as ctx:
            remote_client.get_sms_otp_code()
        self.assertIn("try again", ctx.exception.hint)
        self.assertIn("Read timed out", ctx.exception.details)

    def test_sms_request_without_connection(self):
        remote_client = get_remote_client(202)
        remote_client.manager.post.side_effect = RequestsConnectionError("Name or service not known")

        with self.assertRaises(SmsRequestException) as ctx:
            remote_client.get_sms_otp_code()
        self.assertIn("internet connection", ctx.exception.hint)


if __name__ == '__main__':
    unittest.main()
