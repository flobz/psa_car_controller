import argparse
import atexit
import logging
import socket
import threading
from os import environ, path

import psa_car_controller
from oauth2_client.credentials_manager import OAuthError

from .charge_control import ChargeControls
from .charging import Charging
from psa_car_controller.psacc.repository.config_repository import ConfigRepository
from psa_car_controller.psacc.utils.utils import Singleton
from .psa_client import PSAClient
from psa_car_controller.common.mylogger import my_logger
from psa_car_controller.psa.otp.otp import CONFIG_NAME as OTP_CONFIG_NAME, ConfigException
from psa_car_controller import __version__

DEFAULT_NAME = "config.json"

logger = logging.getLogger(__name__)


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
    parser.add_argument('--version', action='version', version='PSACC {}'.format(psa_car_controller.__version__))

    return parser.parse_args()


class PSACarController(metaclass=Singleton):
    def __init__(self):
        self.args = parse_args()
        self.myp: PSAClient
        self.chc: ChargeControls
        self.config_name = DEFAULT_NAME
        self.is_good: bool = True
        self.offline = self.args.offline
        self.remote_control = not (self.args.remote_disable or self.offline)
        self.config = ConfigRepository.read_config()

    def start_remote_control(self):
        if self.args.remote_disable:
            logger.info("mqtt disabled")
        elif not self.args.web_conf or path.isfile(OTP_CONFIG_NAME):
            if self.myp.remote_client.mqtt_client is not None:
                self.myp.remote_client.mqtt_client.disconnect()
            try:
                self.myp.remote_client.start()
                if self.args.charge_control:
                    self.chc = ChargeControls.load_config(self.myp, name=self.args.charge_control)
                    self.chc.init()
                    self.myp.start_refresh_thread()
            except socket.timeout:
                logger.error("Can't connect to mqtt broker your are not connected to internet or PSA MQTT server is "
                             "down !")
            except ConfigException:
                logger.error("start_remote_control failed redo otp config")

    def load_app(self) -> bool:
        # pylint: disable=too-many-branches
        my_logger(handler_level=int(self.args.debug))
        
        logger.info("App version %s", __version__)
        if self.args.config:
            self.config_name = self.args.config
        if path.isfile(self.config_name):
            self.myp = PSAClient.load_config(name=self.config_name)
        elif self.args.web_conf:
            logger.error("No config file")
            self.is_good = False
            return False
        else:
            raise FileNotFoundError(self.config_name)
        atexit.register(self.save_config)
        self.myp.set_record(self.args.record)
        Charging.elec_price = self.config.Electricity_config
        if self.args.offline:
            logger.info("offline mode")
            self.is_good = True
        else:
            self.is_good = False
            try:
                self.is_good = self.myp.manager.refresh_token_now()
                if self.is_good:
                    logger.info(str(self.myp.get_vehicles()))
            except OAuthError:
                if self.args.mail and self.args.password:
                    self.myp.connect(self.args.mail, self.args.password)
                    logger.info(str(self.myp.get_vehicles()))
                    self.is_good = True
                else:
                    self.is_good = False
                    if self.args.web_conf:
                        logger.error("Please reconnect by going to config web page")
                    else:
                        logger.error("Connection need to be updated, Please redo authentication process.")
            if self.args.refresh:
                self.myp.info_refresh_rate = self.args.refresh * 60
                if self.is_good:
                    self.myp.start_refresh_thread()
            if self.is_good:
                self.start_remote_control()
            elif not self.args.web_conf:
                raise ConnectionError
        self.save_config()
        return True

    def save_config(self):
        threading.Timer(30, self.save_config).start()
        self.myp.save_config(self.config_name)
