"""Reconnecting from the config page while the brand login service (GetAccessToken) is down.

That service only provides the customer id and the car labels, and it has failed for hours
at a time while the OAuth login, which provides the tokens, kept working.
"""
import unittest
from unittest.mock import MagicMock, patch

from psa_car_controller.psa.constants import BRAND
from psa_car_controller.psa.setup.app_decoder import InitialSetup

PEUGEOT = "com.psa.mym.mypeugeot"


class TestReconnectWithoutBrandLogin(unittest.TestCase):
    @staticmethod
    def setup(existing_config):
        broken = MagicMock()
        broken.json.side_effect = ValueError("not json")
        broken.text = 'SoapFault exception: [HTTP] Could not connect to host {"returnCode":"NEED_ACTIVATION"}'
        module = "psa_car_controller.psa.setup.app_decoder"
        with patch(module + ".get_content_from_apk"), \
                patch(module + ".requests.post", return_value=broken), \
                patch(module + ".path.isfile", return_value=existing_config is not None), \
                patch(module + ".PSAClient.load_config", return_value=existing_config):
            return InitialSetup(PEUGEOT, "user@example.com", "password", "FR")

    def test_reuses_the_existing_configuration(self):
        existing = MagicMock(realm=BRAND[PEUGEOT]["realm"], customer_id="AP-1234")
        setup = self.setup(existing)
        self.assertIs(existing, setup.psacc)
        self.assertEqual("AP-1234", setup.customer_id)
        self.assertIsNone(setup.user_info)

    def test_fails_with_a_short_message_without_configuration(self):
        with self.assertRaises(ConnectionError) as error:
            self.setup(None)
        self.assertIn("try again later", str(error.exception))
        self.assertNotIn("Traceback", str(error.exception))

    def test_ignores_the_configuration_of_another_brand(self):
        with self.assertRaises(ConnectionError):
            self.setup(MagicMock(realm=BRAND["com.psa.mym.myopel"]["realm"]))


if __name__ == '__main__':
    unittest.main()
