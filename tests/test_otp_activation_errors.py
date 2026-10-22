"""Errors of the OTP server during the remote control activation get an explanation.

Before, the OTP config page only showed the raw answer, for instance
"Error during activation finalize: {'newversion': None, 'newversionurl': None, 'err': 'NOK:MAXNBTOOLS'}".
"""
import unittest
from unittest.mock import patch

from psa_car_controller.psa.otp.otp import ActivationException, ConfigException, Otp
from psa_car_controller.web.tools.utils import create_error_alert

MAXNBTOOLS = {"newversion": None, "newversionurl": None, "err": "NOK:MAXNBTOOLS"}


def get_otp() -> Otp:
    otp = Otp("bb8e981582b0f31353108fb020bead1c")
    otp.smsCode = "123456"
    otp.codepin = "1234"
    return otp


def alert_text(alert) -> str:
    def text(component):
        if isinstance(component, str):
            return component
        children = getattr(component, "children", None)
        if isinstance(children, list):
            return " ".join(text(child) for child in children)
        return text(children) if children is not None else ""
    return text(alert)


class TestActivationException(unittest.TestCase):

    def test_too_many_devices_explains_how_to_reset_them(self):
        error = ActivationException("finalize", MAXNBTOOLS)
        self.assertEqual("NOK:MAXNBTOOLS", error.code)
        self.assertIn("maximum number of devices", error.hint)
        self.assertIn("reinstall the phone app", error.hint)

    def test_unknown_code_gets_a_generic_hint(self):
        error = ActivationException("finalize", {"err": "NOK:SOMETHING"})
        self.assertIn("NOK:SOMETHING", error.hint)
        self.assertIn("PIN", error.hint)

    def test_message_keeps_the_raw_answer_for_the_log(self):
        error = ActivationException("finalize", MAXNBTOOLS)
        self.assertIn("NOK:MAXNBTOOLS", str(error))
        self.assertIsInstance(error, ConfigException)  # existing handlers still catch it

    def test_activation_start_raises_it(self):
        otp = get_otp()
        with patch.object(otp, "request", return_value=MAXNBTOOLS):
            with self.assertRaises(ActivationException) as ctx:
                otp.activation_start()
        self.assertEqual("NOK:MAXNBTOOLS", ctx.exception.code)


class TestErrorAlert(unittest.TestCase):

    def test_shows_title_hints_link_and_details(self):
        error = ActivationException("finalize", MAXNBTOOLS)
        alert = create_error_alert("The remote control could not be activated", [error.hint, "Second hint"],
                                   str(error), ("More in the FAQ", "https://example.invalid/faq"))
        text = alert_text(alert)
        self.assertEqual("warning", alert.color)
        for expected in ("could not be activated", "maximum number of devices", "Second hint",
                         "More in the FAQ", "NOK:MAXNBTOOLS"):
            self.assertIn(expected, text)


if __name__ == '__main__':
    unittest.main()
