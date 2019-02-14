#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import logging
import re
from datetime import datetime, timedelta

from atraxiflow.core.exceptions import ValueException


def dict_read_from_path(d, path):
    '''
    Returns an item from a dict using a path (like: foo.bar.elem)
    :param d: dict
    :param path: str
    :return: object
    '''

    if not isinstance(d, dict):
        raise ValueError('First argument needs to be of type dict.')

    if path.find('.') == -1:
        return d[path]
    else:
        parts = path.split('.')
        deeper = d
        for p in parts:
            if p in deeper.keys():
                deeper = deeper[p]
            else:
                raise ValueException('Could not find "{0}" in dictionary'.format(path))

        return deeper


class DatetimeProcessor:
    def processString(str):
        if "today" == str:
            return datetime.now()
        elif "yesterday" == str:
            return datetime.now() - timedelta(days=1)
        else:
            return datetime.strptime(str)


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
                logging.debug("Could not resolve variable '%s'".format(var))
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
