
import logging

class ColoredFormatter(logging.Formatter):
    green = '\u001b[32m'
    grey = '\u001b[36m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'
    splitter = '\n' + '-' * 100

    def __init__(self, *args, **kwargs):
        super(ColoredFormatter, self).__init__(*args, **kwargs)
        self._level_color_format = {
            logging.NOTSET: self.reset + "{}" + self.reset,
            logging.DEBUG: self.grey + "{}" + self.reset,
            logging.INFO: self.blue + "{}" + self.reset,
            logging.WARNING: self.yellow + "{}" + self.reset,
            logging.ERROR: self.red + "{}" + self.reset,
            logging.CRITICAL: self.bold_red + "{}" + self.reset,
        }
        self._message_color_format = self.green + "{}" + self.reset

    def format(self, record: logging.LogRecord) -> str:
        record.levelname = self._level_color_format.get(
            record.levelno, "").format(record.levelname)
        record.msg = self._message_color_format.format(record.msg)
        return super(ColoredFormatter, self).format(record) + self.splitter
    
def logger_creator(
        name, 
        stream_level=logging.DEBUG):
    logger = logging.getLogger(name)
    console_format = '[%(levelname)s] %(asctime)s-FILENAME:%(filename)s-MODULE:%(module)s-FUNC:%(funcName)s :: \n%(message)s'
    console_formatter = ColoredFormatter(
        console_format,
        datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler()
    logger = logger_settings(
        console_handler, stream_level, console_formatter, logger
    )
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger

def logger_settings(handler, level, formatter, logger):
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
