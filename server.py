import threading
from datetime import timedelta
from threading import Thread

from oauth2_client.credentials_manager import OAuthError

from ChargeControl import ChargeControls
from MyPSACC import *
from flask import Flask, request, jsonify
import argparse
parser = argparse.ArgumentParser()

app = Flask(__name__)

@app.route('/getvehicules')
def getvehicules():
    return jsonify(myp.getVIN())

@app.route('/get_vehiculeinfo/<string:vin>')
def getVehiculeInfo(vin):
    response = app.response_class(
        response=json.dumps(myp.getVehiculeinfo(vin).to_dict(),default=str),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/charge_now/<string:vin>/<int:charge>')
def chargeNow(vin,charge):
    return jsonify(myp.charge_now(vin,charge != 0 ))

@app.route('/charge_hour')
def change_charge_hour():
    return jsonify(myp.change_charge_hour(request.form['vin'],request.form['hour'],request.form['minute']))

@app.route('/wakeup/<string:vin>')
def wakeup(vin):
    return jsonify(myp.wakeup(vin))

@app.route('/preconditioning/<string:vin>/<int:activate>')
def preconditioning(vin, activate):
    return jsonify(myp.preconditioning(vin, activate))

def saveconfig(mypeugeot:MyPSACC):
    myp.saveconfig()
    threading.Timer(30, saveconfig, args=[mypeugeot]).start()

#Set a battery threshold and schedule an hour to stop the charge
@app.route('/charge_control')
def charge_control():
    print(request)
    vin = request.args['vin']
    charge_control = chc.get(vin)
    if charge_control is None:
        return jsonify("error: VIN not in list")
    if 'hour' in request.args or 'minute' in request.args:
        charge_control.set_stop_hour([int(request.args["hour"]), int(request.args["minute"])])
    if 'percentage' in request.args :
        charge_control.percentage_threshold = int(request.args['percentage'])
    chc.saveconfig()
    return jsonify(charge_control.get_dict())

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--config", help="config file",type  = argparse.FileType('r'))
    parser.add_argument("-c","--charge-control", help="enable charge control",action="store_true")
    parser.parse_args()
    return parser

if __name__ == "__main__":
    parser = parse_args()
    args = parser.parse_args()
    print(args.__dict__)
    if args.config:
        myp = MyPSACC.loadconfig(name=args.config.name)
    else:
        myp = MyPSACC.loadconfig()
    try:
        myp.manager._refresh_token()
    except OAuthError:
        client_email = input("mypeugeot email: ")
        client_paswword = input("mypeugeot password: ")
        myp.connect(client_email,client_paswword)
    print(myp.get_vehicles())
    myp.startmqtt()
    t1=Thread(target=app.run)
    t1.start()
    saveconfig(myp)
    if args.charge_control:
        chc = ChargeControls.load_config(myp)
        chc.start()
