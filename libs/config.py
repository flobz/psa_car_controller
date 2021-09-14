import argparse
import atexit
import threading
from os import environ, path

from oauth2_client.credentials_manager import OAuthError

from charge_control import ChargeControls
from libs.charging import Charging
from libs.elec_price import ElecPrice
from my_psacc import MyPSACC
from mylogger import logger, my_logger
from otp.otp import CONFIG_NAME as OTP_CONFIG_NAME

DEFAULT_NAME = "config.json"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config", help="config file, default file: config.json", default="config.json")
    parser.add_argument("-c", "--charge-control", help="enable charge control, default charge_config.json",
                        const="charge_config.json", nargs='?', metavar='charge config file')
    parser.add_argument("-d", "--debug", help="enable debug", const=10, default=20, nargs='?',
                        metavar='Debug level number or name')
    parser.add_argument("-l", "--listen", help="change server listen address", default="127.0.0.1", metavar="IP")
    parser.add_argument("-p", "--port", help="change server listen port", default="5000")
    parser.add_argument("-r", "--record", help="save vehicle data to db", action='store_true')
    parser.add_argument("-R", "--refresh", help="refresh vehicles status every x min", type=int)
    parser.add_argument("-m", "--mail", default=environ.get('USER_EMAIL', None), help="set the email address")
    parser.add_argument("-P", "--password", default=environ.get('USER_PASSWORD', None), help="set the password")
    parser.add_argument("--remote-disable", help="disable remote control", action='store_true')
    parser.add_argument("--offline", help="offline limited mode", action='store_true')
    parser.add_argument("--web-conf", help="ignore if config files not existing yet", action='store_true')
    parser.add_argument("-b", "--base-path", help="base path for web app", default="/")
    return parser.parse_args()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=Singleton):
    def __init__(self):
        self.args = parse_args()
        self.myp: MyPSACC
        self.chc: ChargeControls
        self.config_name = DEFAULT_NAME
        self.is_good: bool = False
        self.offline = self.args.offline
        self.remote_control = not (self.args.remote_disable or self.offline)

    def start_remote_control(self):
        if self.args.remote_disable:
            logger.info("mqtt disabled")
        elif not self.args.web_conf or path.exists(OTP_CONFIG_NAME):
            if self.myp.mqtt_client is not None:
                self.myp.mqtt_client.disconnect()
            self.myp.start_mqtt()
            if self.args.charge_control:
                Config.chc = ChargeControls.load_config(self.myp, name=self.args.charge_control)
                Config.chc.init()
                self.myp.start_refresh_thread()

    def load_app(self) -> bool:
        my_logger(handler_level=int(self.args.debug))
        if self.args.config:
            self.config_name = self.args.config
        if path.exists(self.config_name):
            self.myp = MyPSACC.load_config(name=self.config_name)
        elif self.args.web_conf:
            return False
        else:
            raise FileNotFoundError(self.config_name)
        atexit.register(self.save_config)
        self.myp.set_record(self.args.record)
        Charging.elec_price = ElecPrice.read_config()
        if self.args.offline:
            logger.info("offline mode")
        else:
            try:
                self.myp.refresh_token()
            except OAuthError:
                if self.args.mail and self.args.password:
                    self.myp.connect(self.args.mail, self.args.password)
                else:
                    logger.error("Please reconnect by going to config web page")
            logger.info(str(self.myp.get_vehicles()))
            if self.args.refresh:
                self.myp.info_refresh_rate = self.args.refresh * 60
                self.myp.start_refresh_thread()
            self.start_remote_control()
        self.save_config()
        self.is_good = True
        return True

    def save_config(self):
        self.myp.save_config(self.config_name)
        threading.Timer(30, self.save_config).start()
