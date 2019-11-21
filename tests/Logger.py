import logging


class Logger:
    loggers = {}

    @staticmethod
    def get_logger(router="main") -> logging.Logger:
        if router in Logger.loggers:
            return Logger.loggers[router]

        new_logger = logging.getLogger(router)
        handler = logging.FileHandler('/logs/{router}.log'.format(router=router))
        handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
        new_logger.addHandler(handler)
        Logger.loggers[router] = new_logger

        return Logger.loggers[router]
