#!/usr/bin/env python3
import atexit
import sys
from os import environ
from threading import Thread
from getpass import getpass
import argparse

from oauth2_client.credentials_manager import OAuthError


import web.app
from charge_control import ChargeControls
from libs.charging import Charging
from libs.elec_price import ElecPrice
from mylogger import my_logger
from mylogger import logger
from my_psacc import MyPSACC
from utils import is_port_in_use
from web.app import start_app, save_config

CONFIG_NAME = "config.json"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config", help="config file, default file: config.json", type=argparse.FileType('r'),
                        default="config.json")
    parser.add_argument("-c", "--charge-control", help="enable charge control, default charge_config.json",
                        const="charge_config.json", nargs='?', metavar='charge config file')
    parser.add_argument("-d", "--debug", help="enable debug", const=10, default=20, nargs='?',
                        metavar='Debug level number', type=int)
    parser.add_argument("-l", "--listen", help="change server listen address", default="127.0.0.1", metavar="IP")
    parser.add_argument("-p", "--port", help="change server listen port", default="5000")
    parser.add_argument("-r", "--record", help="save vehicle data to db", action='store_true')
    parser.add_argument("-R", "--refresh", help="refresh vehicles status every x min", type=int)
    parser.add_argument("-m", "--mail", default=environ.get('USER_EMAIL', None), help="set the email address")
    parser.add_argument("-P", "--password", default=environ.get('USER_PASSWORD', None), help="set the password")
    parser.add_argument("--remote-disable", help="disable remote control", action='store_true')
    parser.add_argument("--offline", help="offline limited mode", action='store_true')
    parser.add_argument("-b", "--base-path", help="base path for web app", default="/")
    return parser.parse_args()


# flake8: noqa: C901
if __name__ == "__main__":
    if sys.version_info < (3, 6):
        raise RuntimeError("This application requires Python 3.6+")
    args = parse_args()
    my_logger(handler_level=args.debug)
    if is_port_in_use(args.listen, int(args.port)):
        logger.error(" Address already in use")
        sys.exit(1)
    logger.info("server start")
    if args.config:
        CONFIG_NAME = args.config.name
    web.app.myp = MyPSACC.load_config(name=CONFIG_NAME)
    atexit.register(web.app.myp.save_config)
    web.app.myp.set_record(args.record)
    Charging.elec_price = ElecPrice.read_config()
    if args.offline:
        logger.info("offline mode")
    else:
        try:
            web.app.myp.refresh_token()
        except OAuthError:
            if args.mail and args.password:
                client_email = args.mail
                client_password = args.password
            else:
                client_email = input(f"{web.app.myp.get_app_name()} email: ")
                client_password = getpass(f"{web.app.myp.get_app_name()} password: ")
            web.app.myp.connect(client_email, client_password)
        logger.info(str(web.app.myp.get_vehicles()))
        if args.remote_disable:
            logger.info("mqtt disabled")
        else:
            web.app.myp.start_mqtt()
        if args.refresh or args.charge_control:
            if args.refresh:
                web.app.myp.info_refresh_rate = args.refresh * 60
            if args.charge_control:
                web.app.chc = ChargeControls.load_config(web.app.myp, name=args.charge_control)
                web.app.chc.init()
            t2 = Thread(target=web.app.myp.refresh_vehicle_info)
            t2.setDaemon(True)
            t2.start()

    save_config(web.app.myp, CONFIG_NAME)
    t1 = Thread(target=start_app, args=["My car info", args.base_path, logger.level < 20, args.listen, int(args.port)])
    t1.setDaemon(True)
    t1.start()
