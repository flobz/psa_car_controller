#!/usr/bin/env python3
import json
import os
import traceback
from os import path

from androguard.core.bytecodes.apk import APK
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

from charge_control import ChargeControl, ChargeControls
from my_psacc import MyPSACC
from mylogger import logger

BRAND = {"com.psa.mym.myopel": {"realm": "clientsB2COpel", "brand_code": "OP", "app_name": "MyOpel"},
         "com.psa.mym.mypeugeot": {"realm": "clientsB2CPeugeot", "brand_code": "AP", "app_name": "MyPeugeot"},
         "com.psa.mym.mycitroen": {"realm": "clientsB2CCitroen", "brand_code": "AC", "app_name": "MyCitroen"},
         "com.psa.mym.myds": {"realm": "clientsB2CDS", "brand_code": "DS", "app_name": "MyDS"},
         "com.psa.mym.myvauxhall": {"realm": "clientsB2CVauxhall", "brand_code": "VX", "app_name": "MyVauxhall"}
         }
DOWNLOAD_URL = "https://github.com/flobz/psa_apk/raw/main/"
APP_VERSION = "1.33.0"


def save_key_to_pem(pfx_data, pfx_password):
    private_key, certificate = pkcs12.load_key_and_certificates(pfx_data,
                                                                pfx_password, default_backend())[:2]
    try:
        os.mkdir("certs")
    except FileExistsError:
        pass
    with open("certs/public.pem", "wb") as f:
        f.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))

    with open("certs/private.pem", "wb") as f:
        f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PrivateFormat.TraditionalOpenSSL,
                                          encryption_algorithm=serialization.NoEncryption()))


def urlretrieve(url, path):
    with open(path, 'wb') as f:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        for chunk in r.iter_content(1024):
            f.write(chunk)


def get_cultures_code(file, country_code):
    cultures = json.loads(file)
    return cultures[country_code]["languages"][0]


def firstLaunchConfig(package_name, client_email, client_password, country_code,  # pylint: disable=too-many-locals
                      config_prefix=""):
    filename = package_name.split(".")[-1] + ".apk"
    if not path.exists(filename):
        urlretrieve(DOWNLOAD_URL + filename, filename)
    a = APK(filename)
    package_name = a.get_package()
    resources = a.get_android_resources()  # .get_strings_resources()
    client_id = resources.get_string(package_name, "PSA_API_CLIENT_ID_PROD")[1]
    client_secret = resources.get_string(package_name, "PSA_API_CLIENT_SECRET_PROD")[1]
    HOST_BRANDID_PROD = resources.get_string(package_name, "HOST_BRANDID_PROD")[1]
    REMOTE_REFRESH_TOKEN = None
    culture = get_cultures_code(a.get_file("res/raw/cultures.json"), country_code)
    ## Get Customer id
    site_code = BRAND[package_name]["brand_code"] + "_" + country_code + "_ESP"
    pfx_cert = a.get_file("assets/MWPMYMA1.pfx")
    save_key_to_pem(pfx_cert, b"y5Y2my5B")
    try:
        res = requests.post(HOST_BRANDID_PROD + "/GetAccessToken",
                            headers={
                                "Connection": "Keep-Alive",
                                "Content-Type": "application/json",
                                "User-Agent": "okhttp/2.3.0"
                            },
                            params={"jsonRequest": json.dumps(
                                {"siteCode": site_code, "culture": "fr-FR", "action": "authenticate",
                                 "fields": {"USR_EMAIL": {"value": client_email},
                                            "USR_PASSWORD": {"value": client_password}}
                                 }
                            )}
                            )

        token = res.json()["accessToken"]
    except Exception as ex:
        msg = traceback.format_exc() + f"\nHOST_BRANDID : {HOST_BRANDID_PROD} sitecode: {site_code}"
        try:
            msg += res.text
        except:  # pylint: disable=bare-except
            pass
        logger.error(msg)
        raise Exception(msg) from ex
    try:
        res2 = requests.post(
            f"https://mw-{BRAND[package_name]['brand_code'].lower()}-m2c.mym.awsmpsa.com/api/v1/user",
            params={
                "culture": culture,
                "width": 1080,
                "version": APP_VERSION
            },
            data=json.dumps({"site_code": site_code, "ticket": token}),
            headers={
                "Connection": "Keep-Alive",
                "Content-Type": "application/json;charset=UTF-8",
                "Source-Agent": "App-Android",
                "Token": token,
                "User-Agent": "okhttp/4.8.0",
                "Version": APP_VERSION
            },
            cert=("certs/public.pem", "certs/private.pem"),
        )

        res_dict = res2.json()["success"]
        customer_id = BRAND[package_name]["brand_code"] + "-" + res_dict["id"]
    except Exception as ex:
        msg = traceback.format_exc()
        try:
            msg += res2.text
        except:  # pylint: disable=bare-except
            pass
        logger.error(msg)
        raise Exception(msg) from ex
    # Psacc
    psacc = MyPSACC(None, client_id, client_secret, REMOTE_REFRESH_TOKEN, customer_id, BRAND[package_name]["realm"],
                    country_code)
    psacc.connect(client_email, client_password)
    psacc.save_config(name=config_prefix + "config.json")
    res = psacc.get_vehicles()

    if len(res) == 0:
        Exception("No vehicle in your account is compatible with this API, you vehicle is probably too old...")

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
