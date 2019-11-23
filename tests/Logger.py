import logging
import sys

file_logging_level = logging.DEBUG
stdout_logging_level = logging.DEBUG

class Logger:
    loggers = {}

    @staticmethod
    def get_logger(router: str) -> logging.Logger:
        if router in Logger.loggers:
            return Logger.loggers[router]

        new_logger = logging.getLogger(router)
        new_logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-6s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        file_handler = logging.FileHandler('logs/{router}.log'.format(router=router))
        file_handler.setFormatter(formatter)
        file_handler.setLevel(file_logging_level)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        stdout_handler.setLevel(stdout_logging_level)

        new_logger.addHandler(file_handler)
        new_logger.addHandler(stdout_handler)
        Logger.loggers[router] = new_logger

        return Logger.loggers[router]
