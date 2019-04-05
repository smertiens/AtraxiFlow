#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import re
from datetime import datetime, timedelta


class DatetimeProcessor:

    def get_logger(self):
        '''
        Returns the classes logger
        :return: Logger
        '''
        return logging.getLogger(DatetimeProcessor.__module__)

    def process_string(self, date_str):
        if 'today' == date_str:
            return datetime.now()
        elif 'yesterday' == date_str:
            return datetime.now() - timedelta(days=1)
        elif 'tomorrow' == date_str:
            return datetime.now() + timedelta(days=1)
        else:
            fmt = ''
            # Determine datetime format
            # European date format (dd.mm.YY / YYYY)
            res = re.match(r'^\d{2}.\d{2}.\d{2}(\d{2})*( \d{2}:\d{2}(:\d{2})*)*$', date_str)
            if res:
                if res.groups()[0] == None:
                    fmt = '%d.%m.%y'
                else:
                    fmt = '%d.%m.%Y'

                if res.groups()[1] is not None:
                    fmt += ' %H:%M'

                if res.groups()[2] is not None:
                    fmt += ':%S'

            # American date format (mmm/dd/YY / YYYY)
            res = re.match(r'^\d{2}/\d{2}/\d{2}(\d{2})*( \d{2}:\d{2}(:\d{2})*)*$', date_str)
            if res:
                if res.groups()[0] == None:
                    fmt = '%m/%d/%y'
                else:
                    fmt = '%m/%d/%Y'

                if res.groups()[1] is not None:
                    fmt += ' %H:%M'

                if res.groups()[2] is not None:
                    fmt += ':%S'

            if fmt == '':
                self.get_logger().error('Unrecognized date/time format: {0}. Using current date/time.'.format(date_str))
                return datetime.now()

            return datetime.strptime(date_str, fmt)


class StringValueProcessor:

    def __init__(self, stream):
        """

        :type stream: Stream
        """
        self.stream = stream
        self._value_map = {}

    def add_variable(self, key, value):
        self._value_map[key] = value
        return self

    def parse(self, string):
        """

        :type string: str
        """
        matches = re.findall("{(.+?)}", string)

        for match in matches:
            string = string.replace("{" + match + "}", self._get_variable_value(match))

        return string

    def _get_variable_value(self, var):
        """

        :type var: str
        """

        try:
            (prefix, key) = var.split(":")
        except ValueError:
            # No namespace given - assert local variable
            if var in self._value_map:
                return self._value_map[var]
            else:
                logging.debug("Could not resolve variable {0}'".format(var))
                return ""

        res_name = key
        # if key contains ., we take the first part as resource name
        if res_name.find('.') > -1:
            res_name = res_name[0:res_name.find('.')]

        result = self.stream.get_resources("{0}:{1}".format(prefix, res_name))

        if not result or not isinstance(result, list):
            return ''

        res = result[0]

        # request the variable from the resource - not used yet
        if key == res.get_name():
            return res.get_data()
        else:
            return res.resolve_variable(key)
