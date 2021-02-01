#!/usr/bin/env python3
import json
import os
import traceback

from androguard.core.bytecodes.apk import APK

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

from ChargeControl import ChargeControl, ChargeControls
from MyPSACC import MyPSACC
from sys import argv
import sys
import re

BRAND = {"clientsB2CPeugeot": "AP", "clientsB2CCitroen": "AC", "clientsB2CDS": "AC", "clientsB2COpel": "OP",
         "clientsB2CVauxhall": "0V"}

def getxmlvalue(root, name):
    for child in root.findall("*[@name='" + name + "']"):
        return child.text


def find_app_path():
    base_dir = 'apps/'
    paths = os.listdir(base_dir)
    if len(paths) > 0:
        for path in paths:
            pattern = re.compile('com.psa.mym.\\w*')
            print(pattern.match(path))
            if pattern.match(path) is not None:
                return base_dir + path
    return None


def find_preferences_xml():
    paths = os.listdir()
    if len(paths) > 0:
        for path in paths:
            pattern = re.compile('com.psa.mym.\\w*_preferences.xml')
            if pattern.match(path) is not None:
                return path
    return None


def save_key_to_pem(pfx_data, pfx_password):
    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(pfx_data,
                                                                                         bytes.fromhex(pfx_password),
                                                                                         default_backend())
    with open("public.pem", "wb") as f:
        f.write(certificate.public_bytes(encoding=serialization.Encoding.PEM))

    with open("private.pem", "wb") as f:
        f.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                          format=serialization.PrivateFormat.TraditionalOpenSSL,
                                          encryption_algorithm=serialization.NoEncryption()))


current_dir = os.getcwd()
script_dir = dir_path = os.path.dirname(os.path.realpath(__file__))
if sys.version_info < (3, 6):
    raise RuntimeError("This application requres Python 3.6+")

if not argv[1].endswith(".apk"):
    print("No apk given")
    exit(1)
print("APK loading...")
a = APK(argv[1])
package_name = a.get_package()
resources = a.get_android_resources()  # .get_strings_resources()
client_id = resources.get_string(package_name, "PSA_API_CLIENT_ID_PROD")[1]
client_secret = resources.get_string(package_name, "PSA_API_CLIENT_SECRET_PROD")[1]
HOST_BRANDID_PROD = resources.get_string(package_name, "HOST_BRANDID_PROD")[1]
pfx_cert = a.get_file("assets/MWPMYMA1.pfx")
remote_refresh_token = None
print("APK loaded !")

client_email = input("mypeugeot email: ")
client_password = input("mypeugeot password: ")

client_realm = input(f"What is the car api realm : {' '.join(BRAND.keys())}\n")
country_code = input("What is your country code ? (ex: FR, GB, DE, ES...)\n")

## Get Customer id
site_code = BRAND[client_realm] + "_" + country_code + "_ESP"
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
                                        "USR_PASSWORD": {"value": client_password}}})
                                }
                            )

    token = res.json()["accessToken"]
except:
    traceback.print_exc()
    print(f"HOST_BRANDID : {HOST_BRANDID_PROD} sitecode: {site_code}")
    print(res.text)
    exit(1)

save_key_to_pem(pfx_cert, "")

#if client_realm == "clientsB2COpel":
 #   site_code = "OV_" + country_code + "_ESP"
try:
    res2 = requests.post("https://mw-ap-m2c.mym.awsmpsa.com/api/v1/user?culture=fr_FR&width=1080&v=1.27.0",
                         data=json.dumps({"site_code": site_code, "ticket": token}),
                         headers={
                             "Connection": "Keep-Alive",
                             "Content-Type": "application/json;charset=UTF-8",
                             "Source-Agent": "App-Android",
                             "Token": token,
                             "User-Agent": "okhttp/4.8.0",
                             "Version": "1.27.0"
                         },
                         cert=("public.pem", "private.pem"),
                         )
    res_dict = res2.json()["success"]
    customer_id = BRAND[client_realm] + "-" + res_dict["id"]

except:
    traceback.print_exc()
    print(res2.text)
    exit(1)

# Psacc

psacc = MyPSACC(None, client_id, client_secret, remote_refresh_token, customer_id, client_realm)
psacc.connect(client_email, client_password)

os.chdir(current_dir)
psacc.save_config(name="test.json")
res = psacc.get_vehicles()
print(f"\nYour vehicles: {res}")

## Charge control
charge_controls = ChargeControls()
for vin, vehicle in res.items():
    chc = ChargeControl(None, vin, 100, [0, 0])
    charge_controls.list[vin] = chc
charge_controls.save_config(name="charge_config1.json")

try:
    os.remove("private.pem")
    os.remove("public.pem")
except:
    print("Error when deleting temp files")

print("Success !!!")
