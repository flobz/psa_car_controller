import logging
from logging.handlers import RotatingFileHandler

DEBUG_LEVELV_NUM = 9
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")

def debugv(self, message, *args, **kws):
    self.log(DEBUG_LEVELV_NUM, message, *args, **kws)


logging.Logger.debugv = debugv

logger = logging.getLogger("log")


def my_logger(file='activity.log', handler_level=logging.INFO):
    global logger

    #logger.setLevel(logging.DEBUG)
    logger.setLevel(handler_level)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(file, 'a', 1000000, 1, encoding='utf8')
    file_handler.setLevel(handler_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(handler_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
