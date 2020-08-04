#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging

import colorama

__all__ = ['AxLoggingConsoleFormatter', 'setup_loggers', 'set_level']

AXFLOW_LOGGING_SETUP = False

class AxLoggingListHandler(logging.Handler):
    records = []

    def __init__(self, level):
        super().__init__(level)
        self.records = []

    def handle(self, record):
        self.records.append(self.format(record))

    def get_records(self, offset = 0):
        return self.records[offset:]

    def clear_records(self):
        self.records.clear()

class AxLoggingConsoleFormatter(logging.Formatter):

    def format(self, record):
        super().format(record)
        txt = ''

        if record.levelno == logging.DEBUG:
            txt += colorama.Style.DIM
        elif record.levelno == logging.WARNING:
            txt += colorama.Fore.YELLOW
        elif record.levelno == logging.ERROR:
            txt += colorama.Fore.RED

        txt += '{} {}: {}'.format(self.formatTime(record, '%H:%M:%S'), record.module, record.getMessage())
        txt += colorama.Style.RESET_ALL
        return txt


def set_level(level):
    if AXFLOW_LOGGING_SETUP == False:
        setup_loggers(level)
        return

    logging.getLogger('core').setLevel(level)
    logging.getLogger('workflow_ctx').setLevel(level)
    logging.getLogger('creator').setLevel(level)


def setup_loggers(level=logging.INFO):
    global AXFLOW_LOGGING_SETUP

    if AXFLOW_LOGGING_SETUP == True:
        logging.getLogger('core').debug('Skipping logger setup. Logging already setup.')
        return

    colorama.init()

    core_logger = logging.getLogger('core')
    ctx_logger = logging.getLogger('workflow_ctx')
    creator_logger = logging.getLogger('creator')

    handler = logging.StreamHandler()
    handler.setFormatter(AxLoggingConsoleFormatter())

    # setup core logger
    core_logger.setLevel(level)
    core_logger.addHandler(handler)

    # setup workflow logger
    ctx_logger.setLevel(level)
    ctx_logger.addHandler(handler)

    # setup creator logger
    creator_logger.setLevel(level)
    creator_logger.addHandler(handler)

    AXFLOW_LOGGING_SETUP = True
