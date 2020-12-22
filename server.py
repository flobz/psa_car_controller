#!/usr/bin/env python3
import atexit
import sys
from threading import Thread

from oauth2_client.credentials_manager import OAuthError

import web.app
from ChargeControl import ChargeControls
from MyLogger import my_logger
import argparse
from MyLogger import logger
from MyPSACC import MyPSACC
from web.app import start_app, save_config

parser = argparse.ArgumentParser()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config", help="config file", type=argparse.FileType('r'))
    parser.add_argument("-c", "--charge-control", help="enable charge control", const="charge_config.json", nargs='?')
    parser.add_argument("-d", "--debug", help="enable debug", const=10, default=20, nargs='?')
    parser.add_argument("-l", "--listen", help="change server listen address", default="127.0.0.1")
    parser.add_argument("-p", "--port", help="change server listen address", default="5000")
    parser.add_argument("-r", "--record-position", help="save vehicle position to db", action='store_true')
    parser.add_argument("-m", "--mail", help="change the email address")
    parser.add_argument("-P", "--password", help="change the password")
    parser.add_argument("--remote-disable", help="disable remote control")
    parser.add_argument("-b", "--base-path", help="base path for app",default="/")
    parser.parse_args()
    return parser


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        raise RuntimeError("This application requires Python 3.6+")
    parser = parse_args()
    args = parser.parse_args()
    my_logger(handler_level=args.debug)
    logger.info("server start")
    if args.config:
        web.app.myp = MyPSACC.load_config(name=args.config.name)
    else:
        web.app.myp = MyPSACC.load_config()
    atexit.register(web.app.save_config)
    if args.record_position:
        web.app.myp.set_record(True)
    try:
        web.app.myp.manager._refresh_token()
    except OAuthError:
        if args.mail and args.password:
            client_email = args.mail
            client_password = args.password
        else:
            client_email = input("mypeugeot email: ")
            client_password = input("mypeugeot password: ")
        web.app.myp.connect(client_email, client_password)
    logger.info(web.app.myp.get_vehicles())
    t1 = Thread(target=start_app, args=["My car info", args.base_path, args.debug == 20, args.listen, int(args.port)])
    t1.start()
    if args.remote_disable:
        logger.info("mqtt disabled")
    else:
        web.app.myp.start_mqtt()
        if args.charge_control:
            web.app.chc = ChargeControls.load_config(web.app.myp, name=args.charge_control)
            web.app.chc.start()
    save_config(web.app.myp)