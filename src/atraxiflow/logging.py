#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging

class AxLoggingConsoleFormatter(logging.Formatter):

    def format(self, record):
        super().format(record)
        return '{} {}: {}'.format(self.formatTime(record, '%H:%M:%S'), record.module, record.getMessage())

def setup_loggers(level = logging.DEBUG):
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


