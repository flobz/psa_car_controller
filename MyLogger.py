import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("log")


def my_logger(file='activity.log', handler_level=logging.INFO):
    global logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(file, 'a', 1000000, 1, encoding='utf8')
    file_handler.setLevel(handler_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(handler_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
