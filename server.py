import sys
import threading
from threading import Thread

from oauth2_client.credentials_manager import OAuthError

from ChargeControl import ChargeControls
from MyLogger import my_logger
from MyPSACC import *
from flask import Flask, request, jsonify
import argparse
from MyLogger import logger

parser = argparse.ArgumentParser()
app = Flask(__name__)


@app.route('/getvehicles')
def getvehicules():
    return jsonify(myp.getVIN())


@app.route('/get_vehicleinfo/<string:vin>')
def get_vehicle_Info(vin):
    response = app.response_class(
        response=json.dumps(myp.get_vehicle_info(vin).to_dict(), default=str),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/charge_now/<string:vin>/<int:charge>')
def charge_now(vin, charge):
    return jsonify(myp.charge_now(vin, charge != 0))


@app.route('/charge_hour')
def change_charge_hour():
    return jsonify(myp.change_charge_hour(request.form['vin'], request.form['hour'], request.form['minute']))


@app.route('/wakeup/<string:vin>')
def wakeup(vin):
    return jsonify(myp.wakeup(vin))


@app.route('/preconditioning/<string:vin>/<int:activate>')
def preconditioning(vin, activate):
    return jsonify(myp.preconditioning(vin, activate))


def save_config(mypeugeot: MyPSACC):
    myp.save_config()
    threading.Timer(30, save_config, args=[mypeugeot]).start()


# Set a battery threshold and schedule an hour to stop the charge
@app.route('/charge_control')
def charge_control():
    logger.info(request)
    vin = request.args['vin']
    charge_control = chc.get(vin)
    if charge_control is None:
        return jsonify("error: VIN not in list")
    if 'hour' in request.args or 'minute' in request.args:
        charge_control.set_stop_hour([int(request.args["hour"]), int(request.args["minute"])])
    if 'percentage' in request.args:
        charge_control.percentage_threshold = int(request.args['percentage'])
    chc.save_config()
    return jsonify(charge_control.get_dict())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config", help="config file", type=argparse.FileType('r'))
    parser.add_argument("-c", "--charge-control", help="enable charge control", const="charge_config.json", nargs='?')
    parser.add_argument("-d", "--debug", help="enable debug", const=10, default=20, nargs='?')
    parser.add_argument("-l", "--listen", help="change server listen address", default="127.0.0.1")
    parser.add_argument("-p", "--port", help="change server listen address", default="5000")
    parser.add_argument("-m", "--mail", help="change the email address")
    parser.add_argument("-P", "--password", help="change the password")
    parser.add_argument("--remote-disable",help="disable remote control")
    parser.parse_args()
    return parser


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        raise RuntimeError("This application requres Python 3.6+")
    parser = parse_args()
    args = parser.parse_args()
    my_logger(handler_level=args.debug)
    logger.info("server start")
    if args.config:
        myp = MyPSACC.load_config(name=args.config.name)
    else:
        myp = MyPSACC.load_config()
    try:
        myp.manager._refresh_token()
    except OAuthError:
        if args.mail and args.password:
            client_email = args.mail
            client_paswword = args.password
        else:
            client_email = input("mypeugeot email: ")
            client_paswword = input("mypeugeot password: ")
        myp.connect(client_email, client_paswword)
    logger.info(myp.get_vehicles())
    t1 = Thread(target=app.run,kwargs={"host":args.listen,"port":int(args.port)})
    t1.start()
    if args.remote_disable:
       logger.info("mqtt disabled")
    else:
        myp.start_mqtt()
        if args.charge_control:
            chc = ChargeControls.load_config(myp, name=args.charge_control)
            chc.start()
    save_config(myp)

