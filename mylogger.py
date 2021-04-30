import logging
from logging.handlers import RotatingFileHandler

DEBUG_LEVELV_NUM = 9
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")


class CustomLogger(logging.Logger):
    # pylint: disable=too-many-arguments
    def __new_style_log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        if kwargs.pop('style', "%") == "{":  # optional
            msg = msg.format(*args)
            args = []
        super()._log(level, msg, args, exc_info, extra, stack_info)

    def debugv(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUG_LEVELV_NUM):
            self.__new_style_log(DEBUG_LEVELV_NUM, msg, args, **kwargs)


logging.setLoggerClass(CustomLogger)
# pylint: disable=invalid-name
logger = logging.getLogger("log")


def my_logger(file='activity.log', handler_level=logging.INFO):
    global logger
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
