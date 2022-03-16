import json
import os

from androguard.core.bytecodes.apk import APK
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from psa.constants import BRAND


class ApkParser:
    def __init__(self, filename, country_code):
        self.country_code = country_code
        self.filename = filename
        self.host_brandid_prod = None
        self.site_code = None
        self.culture = None
        self.client_id = None
        self.client_secret = None

    @staticmethod
    def __get_cultures_code(file, country_code):
        cultures = json.loads(file)
        return cultures[country_code]["languages"][0]

    def retrieve_content_from_apk(self):
        a = APK(self.filename)
        package_name = a.get_package()
        resources = a.get_android_resources()  # .get_strings_resources()
        self.client_id = resources.get_string(package_name, "PSA_API_CLIENT_ID_PROD")[1]
        self.client_secret = resources.get_string(package_name, "PSA_API_CLIENT_SECRET_PROD")[1]
        self.host_brandid_prod = resources.get_string(package_name, "HOST_BRANDID_PROD")[1]
        self.culture = self.__get_cultures_code(a.get_file("res/raw/cultures.json"), self.country_code)
        ## Get Customer id
        self.site_code = BRAND[package_name]["brand_code"] + "_" + self.country_code + "_ESP"
        pfx_cert = a.get_file("assets/MWPMYMA1.pfx")
        save_key_to_pem(pfx_cert, b"y5Y2my5B")


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