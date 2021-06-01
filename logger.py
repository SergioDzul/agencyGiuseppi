# -*- coding: utf-8 -*-
__author__ = 'Sergio Dzul'

import logging
import traceback

# default django logger
logger = logging.getLogger(__name__)


class Logger:
    """
    Custom log class, in the future it can be change the log library
    or a services like aws cloudwatch.
    :param log_lib: log instance class, by default use the django logger
    """

    def __init__(self, log_lib=logger):
        self.log = log_lib

    def info(self, message):
        """
        :param string message:
        """
        self.log.info(message)

    def warning(self, message):
        """
        :param message: string
        """
        self.log.warning(message)


    def error(self, exception, is_message=False):
        """
        We except an Exception or an inherent instance
        :param :class:Exception exception: Exception instance or a simple string
        :param is_message: Boolean, in case of exception parameter is a string pass this value in True
        """
        if not is_message:
            message = exception
        else:
            name = "Exception: {}".format(type(exception).__name__)
            body = "Exception message: {}".format(exception)
            message = f"""
            ${name}
            ${body}
            """
        self.log.error(message)


log = Logger()
