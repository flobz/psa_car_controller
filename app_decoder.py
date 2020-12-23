#!/usr/bin/env python3
import json
import os
import shutil
import xml.etree.ElementTree as ET
import base64
from ChargeControl import ChargeControl, ChargeControls
from MyPSACC import MyPSACC
from sys import argv
import tarfile
import sys
import traceback
import re


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


current_dir = os.getcwd()
script_dir = dir_path = os.path.dirname(os.path.realpath(__file__))
if sys.version_info < (3, 6):
    raise RuntimeError("This application requres Python 3.6+")

if argv[1].endswith(".apk"):
    from androguard.core.bytecodes.apk import APK
    a = APK(argv[1])
    package_name = "com.psa.mym.mypeugeot"
    resources = a.get_android_resources()  # .get_strings_resources()
    client_id = resources.get_string(package_name, "PSA_API_CLIENT_ID_PROD")[1]
    client_secret = resources.get_string(package_name, "PSA_API_CLIENT_SECRET_PROD")[1]
    remote_refresh_token = None
    customer_id = None

else:
    if len(argv) > 2:
        password = argv[2]
    else:
        password = ""
    res = os.system("java --version")
    if res != 0:
        print("You need to install java on your computer : https://www.java.com/fr/download/")
        exit(1)
    os.system(f"java -jar {script_dir}/abe-all.jar unpack {argv[1]} backup.tar {password}")
    my_tar = tarfile.open('backup.tar')
    my_tar.extractall()
    dir = find_app_path()
    os.chdir(dir + "/sp")
    # get client id/secret
    psa_pref = find_preferences_xml()
    root = ET.parse(psa_pref).getroot()
    client_secret = getxmlvalue(root, "CEA_CLIENT_SECRET")
    client_id = getxmlvalue(root, "CEA_CLIENT_ID")
    #get customer id
    remote_info_file = "BASIC_AUTH_CVS.xml"
    root = ET.parse(remote_info_file).getroot()
    customer_id_enc = getxmlvalue(root, "CRYPTED_CUSTOMER_ID")
    customer_id = base64.b64decode(customer_id_enc).decode('utf-8')
    #get remote token
    try:
        root = ET.parse("HUTokenManager.xml").getroot()
    except FileNotFoundError:
        traceback.print_exc()
        print("Do a remote request (start preconditioning for example) to generate a remote refresh token, "
              "make a new backup and relaunch this script")
        exit(1)
    remote_enc = root[0].text
    remote_dec = json.loads(base64.b64decode(remote_enc))
    try:
        if "refresh_token" in remote_dec:
          remote_refresh_token = remote_dec["refresh_token"]
        # Mypeugeot >= 1.26
        else:
          remote_refresh_token = next(iter(remote_dec.values()))["refresh_token"]
    except:
        traceback.print_exc()
        print(remote_dec)



client_email = input("mypeugeot email: ")
client_paswword = input("mypeugeot password: ")
client_realm = input("What is the car api realm : clientsB2CPeugeot, clientsB2CCitroen, clientsB2CDS, clientsB2COpel, clientsB2CVauxhall\n")
psacc = MyPSACC(None, client_id, client_secret, remote_refresh_token, customer_id, client_realm)
psacc.connect(client_email, client_paswword)

os.chdir(current_dir)
psacc.save_config(name="test.json")
res = psacc.get_vehicles()
print(f"\nYour vehicles: {res}")



if not argv[1].endswith(".apk"):
    try:
        os.remove("backup.tar")
        shutil.rmtree('apps')
    except:
        print("Error when deleting temp files")
    charge_controls = ChargeControls()
    for vin,vehicle in res.items():
        chc = ChargeControl(None,vin,100,[0,0])
        charge_controls.list[vin] = chc
    charge_controls.save_config(name="charge_config1.json")



