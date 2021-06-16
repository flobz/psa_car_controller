# flake8: noqa
import os
import threading
import unittest
from time import sleep

import flask
from flask import request
import requests as http_requests
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from libs.charging import Charging
from libs.elec_price import ElecPrice
from my_psacc import MyPSACC
from web.db import Database
from test.utils import get_new_test_db, record_position, DB_DIR, vehicule_list, record_charging

IP = "localhost"
PORT = 5000
URL = f"http://{IP}:{PORT}"


def wait_for_start(driver, url):
    for _ in range(0, 20):
        try:
            driver.get(url)
            break
        except WebDriverException:
            sleep(0.5)


def openTab(driver, n):
    driver.find_element_by_id("tabs").find_elements_by_class_name("nav-item")[n].click()


def getDriver():
    chrome_options = Options()
    if os.environ.get("NO_HEADLESS", "0") != "1":
        chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def shutdown():
    """Shutdown the Werkzeug dev server, if we're using it.
    From http://flask.pocoo.org/snippets/67/"""
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:  # pragma: no cover
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return ""


class ServerThread(threading.Thread):
    init = False

    def run(self):
        import web.app
        web.app.myp = MyPSACC(None, "None", None, None, None, "clientsB2CPeugeot", "FR")
        web.app.myp.vehicles_list = vehicule_list
        Charging.elec_price = ElecPrice.read_config()
        Database.DEFAULT_DB_FILE = DB_DIR
        config = web.app.config_flask("My car info", "/", False, IP, PORT, reloader=False, unminified=False)
        web.app.app.add_url_rule('/exit', 'home', view_func=shutdown_server)
        web.app.run(config)

    def stop(self):
        http_requests.get(URL + "/exit")


class FrontTest(unittest.TestCase):
    def test_trips_only(self):
        get_new_test_db()
        driver = getDriver()
        flask_app = ServerThread()
        record_position()
        flask_app.start()
        wait_for_start(driver, URL)
        assert driver.find_element_by_id("avg_consum_kw").text == "24.2"
        openTab(driver, 1)
        assert "29 km/h" in driver.find_element_by_id("trips-table").text
        flask_app.stop()
        flask_app.join()
        driver.quit()

    def test_charge_only(self):
        get_new_test_db()
        driver = getDriver()
        flask_app = ServerThread()
        record_charging()
        flask_app.start()
        wait_for_start(driver, URL)
        assert driver.find_element_by_id("avg_emission_kw") != "-"
        assert driver.find_element_by_id("avg_chg_speed").text == "18.6"
        openTab(driver, 2)
        assert "18.86 kWh" in driver.find_element_by_id("battery-table").text
        flask_app.stop()
        flask_app.join()
        driver.quit()


if __name__ == '__main__':
    unittest.main()
