#!/usr/bin/env python3
import logging
import os
import sys
from threading import Thread

DIR = os.path.dirname(os.path.realpath(__file__))
if sys.version_info < (3, 6):
    raise RuntimeError("This application requires Python 3.6+")
# pylint: disable=wrong-import-position
from psacc.utils.requirements import TestRequirements

TestRequirements(DIR + "/../requirements.txt").test_requirements()

import web.app
from psacc.application.psa_car_controller import PSACarController

logger = logging.getLogger(__name__)

# noqa: MC0001
if __name__ == "__main__":
    app = PSACarController()
    app.load_app()
    args = app.args
    t1 = Thread(target=web.app.start_app,
                args=["My car info", args.base_path, logger.level < 20, args.listen, int(args.port)], daemon=True)
    t1.start()
    t1.join()
