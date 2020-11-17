import json
import os
import shutil
import xml.etree.ElementTree as ET
import base64

from ChargeControl import ChargeControl, ChargeControls
from MyPSACC import MyPSACC
from sys import argv
import tarfile


def getxmlvalue(root, name):
    for child in root.findall("*[@name='" + name + "']"):
        return child.text


current_dir = os.getcwd()
script_dir = dir_path = os.path.dirname(os.path.realpath(__file__))

if len(argv) > 2:
    password = argv[2]
else:
    password = ""

os.system(f"java -jar {script_dir}/abe-all.jar unpack {argv[1]} backup.tar {password}")
my_tar = tarfile.open('backup.tar')
my_tar.extractall()

dir = "apps/com.psa.mym.mypeugeot"
os.chdir(dir + "/sp")

psa_pref = "com.psa.mym.mypeugeot_preferences.xml"
root = ET.parse(psa_pref).getroot()
client_secret = getxmlvalue(root, "CEA_CLIENT_SECRET")
client_id = getxmlvalue(root, "CEA_CLIENT_ID")

remote_info_file = "BASIC_AUTH_CVS.xml"
root = ET.parse(remote_info_file).getroot()
customer_id_enc = getxmlvalue(root, "CRYPTED_CUSTOMER_ID")
customer_id = base64.b64decode(customer_id_enc).decode('utf-8')

root = ET.parse("HUTokenManager.xml").getroot()
remote_enc = root[0].text
remote_refresh_token = json.loads(base64.b64decode(remote_enc))["refresh_token"]



client_email = input("mypeugeot email: ")
client_paswword = input("mypeugeot password: ")
client_realm = input("What is the car api realm : clientsB2CPeugeot, clientsB2CDS, clientsB2COpel, clientsB2CVauxhall\n")
psacc = MyPSACC(None, client_id, client_secret, remote_refresh_token, customer_id, realm=client_realm)
psacc.connect(client_email, client_paswword)

os.chdir(current_dir)
psacc.save_config(name="test.json")
res = psacc.get_vehicles()
print(f"\nYour vehicles: {res}")

os.remove("backup.tar")
shutil.rmtree('apps')
charge_controls = ChargeControls()
for vin,vehicle in res.items():
    chc = ChargeControl(None,vin,100,[0,0])
    charge_controls.list[vin] = chc
charge_controls.saveconfig(name="charge_config1.json")

