#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import re
from datetime import datetime, timedelta
from typing import Any

from atraxiflow.core import WorkflowContext

__all__ = ['DatetimeProcessor', 'StringValueProcessor']

class DatetimeProcessor:
    """
    This class handles datetime information.
    """

    RANGE_DATE = 'RANGE_DATE'
    RANGE_DATETIME_SHORT = 'RANGE_DATETIME_SHORT'
    RANGE_DATETIME_LONG = 'RANGE_DATETIME_LONG'

    def __init__(self):
        self._range = None

    def get_logger(self) -> logging.Logger:
        '''
        Returns the classes logger
        :return: Logger
        '''
        return logging.getLogger('core')

    def get_range(self) -> str:
        """
        Returns the precision of the datetime object.
        This is important for comparisons, since all numbers that are not covered by the given range
        have to be set to 0.
        :return: Type of range
        """
        return self._range

    def process_string(self, date_str: str) -> datetime:
        """
        Processes a string as date/datetime.

        :param str date_str: THe string to parse
        :return: A datetime object
        """
        if 'today' == date_str:
            self._range = self.RANGE_DATE
            return datetime.now()
        elif 'yesterday' == date_str:
            self._range = self.RANGE_DATE
            return datetime.now() - timedelta(days=1)
        elif 'tomorrow' == date_str:
            self._range = self.RANGE_DATE
            return datetime.now() + timedelta(days=1)
        else:
            fmt = ''
            # Determine datetime format
            # European date format (dd.mm.YY / YYYY)
            res = re.match(r'^\d{2}.\d{2}.\d{2}(\d{2})*( \d{2}:\d{2}(:\d{2})*)*$', date_str)
            if res:
                self._range = self.RANGE_DATE

                if res.groups()[0] is None:
                    fmt = '%d.%m.%y'
                else:
                    fmt = '%d.%m.%Y'

                if res.groups()[1] is not None:
                    self._range = self.RANGE_DATETIME_SHORT
                    fmt += ' %H:%M'

                if res.groups()[2] is not None:
                    self._range = self.RANGE_DATETIME_LONG
                    fmt += ':%S'

            # American date format (mmm/dd/YY / YYYY)
            res = re.match(r'^\d{2}/\d{2}/\d{2}(\d{2})*( \d{2}:\d{2}(:\d{2})*)*$', date_str)
            if res:
                self._range = self.RANGE_DATE
                if res.groups()[0] is None:
                    fmt = '%m/%d/%y'
                else:
                    fmt = '%m/%d/%Y'

                if res.groups()[1] is not None:
                    self._range = self.RANGE_DATETIME_SHORT
                    fmt += ' %H:%M'

                if res.groups()[2] is not None:
                    self._range = self.RANGE_DATETIME_LONG
                    fmt += ':%S'

            if fmt == '':
                self.get_logger().error('Unrecognized date/time format: {0}. Using current date/time.'.format(date_str))
                self._range = self.RANGE_DATETIME_LONG
                return datetime.now()

            return datetime.strptime(date_str, fmt)


class StringValueProcessor:
    """
    This class processes variables in strings.
    Variable values are taken from the current WorkflowContext's symbol table
    """

    def __init__(self, ctx: WorkflowContext):
        self._ctx = ctx
        self._value_map = {}

    def add_variable(self, key, value):
        self._value_map[key] = value
        return self

    def parse(self, string: str) -> str:
        matches = re.findall("{(.+?)}", string)

        for match in matches:
            string = string.replace("{" + match + "}", self._get_variable_value(match))

        return string

    def _get_variable_value(self, var: str) -> Any:
        # Context lookup
        if self._ctx.has_symbol(var):
            return self._ctx.get_symbol(var)

        if var in self._value_map:
            return self._value_map[var]

        raise Exception('Unknown variable: %s' % var)
