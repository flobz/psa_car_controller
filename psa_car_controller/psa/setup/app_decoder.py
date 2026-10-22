#!/usr/bin/env python3
import json
import logging
import traceback
from os import path
from typing import Optional

import requests

from psa_car_controller.psa.constants import BRAND
from psa_car_controller.psa.setup.apk_parser import ApkParser
from psa_car_controller.psa.setup.github import urlretrieve_from_github
from psa_car_controller.psacc.application.car_controller import PSACarController
from psa_car_controller.psacc.application.psa_client import PSAClient, DEFAULT_CONFIG_FILENAME
from psa_car_controller.psacc.application.charge_control import ChargeControl, ChargeControls

logger = logging.getLogger(__name__)

GITHUB_USER = "flobz"
GITHUB_REPO = "psa_apk"
TIMEOUT_IN_S = 30


def get_content_from_apk(filename: str, country_code: str) -> ApkParser:
    urlretrieve_from_github(GITHUB_USER, GITHUB_REPO, "", filename)
    apk_parser = ApkParser(filename, country_code)
    apk_parser.retrieve_content_from_apk()
    return apk_parser


class InitialSetup:
    def __init__(self, package_name, client_email, client_password, country_code):
        self.package_name = package_name
        filename = package_name.split(".")[-1] + ".apk"
        apk_parser = get_content_from_apk(filename, country_code)
        self.culture = apk_parser.culture
        self.site_code = apk_parser.site_code
        self.client_id = apk_parser.client_id
        self.client_secret = apk_parser.client_secret
        self.version = apk_parser.version
        self.country_code = country_code
        self.user_info = None
        self.customer_id = None
        try:
            self.token = self.__fetch_brand_token(apk_parser, client_email, client_password)
            self.user_info = self.__fetch_user_info()
        except ConnectionError:
            # The brand login only provides the customer id and the car labels. When config.json
            # already has them, the OAuth login alone is enough to renew the connection.
            self.psacc = self.__load_existing_config()
            if self.psacc is None:
                raise
            logger.warning("The brand login service failed, renewing only the OAuth tokens of %s",
                           DEFAULT_CONFIG_FILENAME)
            self.customer_id = self.psacc.customer_id
            return
        self.customer_id = BRAND[self.package_name]["brand_code"] + "-" + self.user_info["id"]

        self.psacc = PSAClient(None, self.client_id, self.client_secret,
                               None, self.customer_id, BRAND[self.package_name]["realm"],
                               self.country_code, BRAND[self.package_name]["brand_code"])

    @staticmethod
    def __fetch_brand_token(apk_parser: ApkParser, client_email, client_password) -> str:
        try:
            res = requests.post(apk_parser.host_brandid_prod + "/GetAccessToken",
                                headers={
                                    "Connection": "Keep-Alive",
                                    "Content-Type": "application/json",
                                    "User-Agent": "okhttp/2.3.0"
                                },
                                params={"jsonRequest": json.dumps(
                                    {"siteCode": apk_parser.site_code, "culture": "fr-FR", "action": "authenticate",
                                     "fields": {"USR_EMAIL": {"value": client_email},
                                                "USR_PASSWORD": {"value": client_password}}
                                     }
                                )},
                                timeout=TIMEOUT_IN_S
                                )
            data = res.json()
        except Exception as ex:
            msg = traceback.format_exc() + f"\nHOST_BRANDID : {apk_parser.host_brandid_prod} " \
                f"sitecode: {apk_parser.site_code}"
            try:
                msg += res.text
            except BaseException:
                pass
            logger.error(msg)
            # the details are in the log, the user only needs to know what to do
            raise ConnectionError("The login service of the brand did not answer correctly. This is usually a "
                                  "temporary problem on the Stellantis side, please try again later.") from ex
        token = data.get("accessToken") or data.get("token")
        if not token:
            logger.error("No access token in response: %s", res.text)
            raise ConnectionError(f"The login was refused: {data.get('returnCode', res.text)}")
        return token

    def __load_existing_config(self) -> Optional[PSAClient]:
        if not path.isfile(DEFAULT_CONFIG_FILENAME):
            return None
        try:
            psacc = PSAClient.load_config(DEFAULT_CONFIG_FILENAME)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Can't reuse %s", DEFAULT_CONFIG_FILENAME)
            return None
        if psacc.realm != BRAND[self.package_name]["realm"]:
            # configured for another brand, its customer id doesn't apply
            return None
        return psacc

    def __fetch_user_info(self):
        try:
            res2 = requests.post(
                f"https://mw-{BRAND[self.package_name]['brand_code'].lower()}-m2c.mym.awsmpsa.com/api/v1/user",
                params={
                    "culture": self.culture,
                    "width": 1080,
                    "version": self.version
                },
                data=json.dumps({"site_code": self.site_code, "ticket": self.token}),
                headers={
                    "Connection": "Keep-Alive",
                    "Content-Type": "application/json;charset=UTF-8",
                    "Source-Agent": "App-Android",
                    "Token": self.token,
                    "User-Agent": "okhttp/4.8.0",
                    "Version": self.version
                },
                cert=("certs/public.pem", "certs/private.pem"),
                timeout=TIMEOUT_IN_S
            )

            res_dict = res2.json()["success"]
        except Exception as ex:
            msg = traceback.format_exc()
            try:
                msg += res2.text
            except BaseException:
                pass
            logger.error(msg)
            raise ConnectionError("Can't get the account information from the brand, this is usually a "
                                  "temporary problem on the Stellantis side, please try again later.") from ex
        return res_dict

    def connect(self, code, config_prefix=""):
        self.psacc.connect(code)
        self.psacc.save_config(name=config_prefix + "config.json")
        res = self.psacc.get_vehicles()

        if len(res) == 0:
            raise ValueError(
                "No vehicle in your account is compatible with this API, you vehicle is probably too old...")

        for vehicle in self.user_info["vehicles"] if self.user_info else []:
            if vin := vehicle.get("vin"):
                car = self.psacc.vehicles_list.get_car_by_vin(vin)
                if car is not None and "short_label" in vehicle and car.label == "unknown":
                    car.label = vehicle["short_label"].split(" ")[-1]  # remove new, nouvelle, neu word....
        self.psacc.vehicles_list.save_cars()

        logger.info("\nYour vehicles: %s", res)

        # Charge control
        charge_controls = ChargeControls(config_prefix + "charge_config.json")
        for vehicle in res:
            chc = ChargeControl(self.psacc, vehicle.vin, 100, [0, 0])
            charge_controls[vehicle.vin] = chc
        charge_controls.save_config()
        app = PSACarController()
        app.load_app()
        app.start_remote_control()
