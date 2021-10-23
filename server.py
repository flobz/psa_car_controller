#!/usr/bin/env python3
# pylint: disable=wrong-import-position
import os
import sys
from threading import Thread

from libs.requirements import TestRequirements

DIR = os.path.dirname(os.path.realpath(__file__))
if sys.version_info < (3, 6):
    raise RuntimeError("This application requires Python 3.6+")

TestRequirements(DIR + "/requirements.txt").test_requirements()

import web.app
from libs.config import Config
from mylogger import logger

# noqa: MC0001
if __name__ == "__main__":
    conf = Config()
    conf.load_app()
    args = conf.args
    t1 = Thread(target=web.app.start_app,
                args=["My car info", args.base_path, logger.level < 20, args.listen, int(args.port)])
    t1.setDaemon(True)
    t1.start()
    t1.join()
