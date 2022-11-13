#!/usr/bin/env python3
import os
import sys
from threading import Thread

DIR = os.path.dirname(os.path.realpath(__file__))
if sys.version_info < (3, 7):
    raise RuntimeError("This application requires Python 3.7+")

# pylint: disable=wrong-import-position
from psa_car_controller.psacc.application.car_controller import PSACarController
from psa_car_controller import web
from psa_car_controller.common.mylogger import logger


# noqa: MC0001

def main():
    app = PSACarController()
    app.load_app()
    args = app.args
    t1 = Thread(target=web.app.start_app,
                args=["My car info", args.base_path, logger.level < 20, args.listen, int(args.port)], daemon=True)
    t1.start()
    t1.join()


if __name__ == "__main__":
    main()
