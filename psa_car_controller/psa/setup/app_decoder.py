#!/usr/bin/env python3
import json
import logging
import traceback

import requests

from psa_car_controller.psa.constants import BRAND
from psa_car_controller.psa.setup.apk_parser import ApkParser
from psa_car_controller.psa.setup.github import urlretrieve_from_github
from psa_car_controller.psacc.application.psa_client import PSAClient
from psa_car_controller.psacc.application.charge_control import ChargeControl, ChargeControls

logger = logging.getLogger(__name__)

APP_VERSION = "1.33.0"
GITHUB_USER = "flobz"
GITHUB_REPO = "psa_apk"
TIMEOUT_IN_S = 10


def get_content_from_apk(filename: str, country_code: str) -> ApkParser:
    apk_parser = ApkParser(filename, country_code)
    urlretrieve_from_github(GITHUB_USER, GITHUB_REPO, "", apk_parser.filename)
    apk_parser.retrieve_content_from_apk()
    return apk_parser


def firstLaunchConfig(package_name, client_email, client_password, country_code,  # pylint: disable=too-many-locals
                      config_prefix=""):
    filename = package_name.split(".")[-1] + ".apk"
    apk_parser = get_content_from_apk(filename, country_code)

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

        token = res.json()["accessToken"]
    except Exception as ex:
        msg = traceback.format_exc() + f"\nHOST_BRANDID : {apk_parser.host_brandid_prod} " \
                                       f"sitecode: {apk_parser.site_code}"
        try:
            msg += res.text
        except BaseException:
            pass
        logger.error(msg)
        raise ConnectionError(msg) from ex
    try:
        res2 = requests.post(
            f"https://mw-{BRAND[package_name]['brand_code'].lower()}-m2c.mym.awsmpsa.com/api/v1/user",
            params={
                "culture": apk_parser.culture,
                "width": 1080,
                "version": APP_VERSION
            },
            data=json.dumps({"site_code": apk_parser.site_code, "ticket": token}),
            headers={
                "Connection": "Keep-Alive",
                "Content-Type": "application/json;charset=UTF-8",
                "Source-Agent": "App-Android",
                "Token": token,
                "User-Agent": "okhttp/4.8.0",
                "Version": APP_VERSION
            },
            cert=("certs/public.pem", "certs/private.pem"),
            timeout=TIMEOUT_IN_S
        )

        res_dict = res2.json()["success"]
        customer_id = BRAND[package_name]["brand_code"] + "-" + res_dict["id"]
    except Exception as ex:
        msg = traceback.format_exc()
        try:
            msg += res2.text
        except BaseException:
            pass
        logger.error(msg)
        raise ConnectionError(msg) from ex
    # Psacc
    psacc = PSAClient(None, apk_parser.client_id, apk_parser.client_secret,
                      None, customer_id, BRAND[package_name]["realm"],
                      country_code)
    psacc.connect(client_email, client_password)
    psacc.save_config(name=config_prefix + "config.json")
    res = psacc.get_vehicles()

    if len(res) == 0:
        raise ValueError("No vehicle in your account is compatible with this API, you vehicle is probably too old...")

    for vehicle in res_dict["vehicles"]:
        car = psacc.vehicles_list.get_car_by_vin(vehicle["vin"])
        if car is not None and "short_label" in vehicle and car.label == "unknown":
            car.label = vehicle["short_label"].split(" ")[-1]  # remove new, nouvelle, neu word....
    psacc.vehicles_list.save_cars()

    logger.info("\nYour vehicles: %s", res)

    # Charge control
    charge_controls = ChargeControls(config_prefix + "charge_config.json")
    for vehicle in res:
        chc = ChargeControl(psacc, vehicle.vin, 100, [0, 0])
        charge_controls[vehicle.vin] = chc
    charge_controls.save_config()
    return "Success !!!"
