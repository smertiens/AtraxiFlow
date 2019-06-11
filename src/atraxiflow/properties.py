#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

class Property:

    def __init__(self, value=None, expected_type=str, default='', required=False, label='', hint=''):
        self._value = value
        self._type = expected_type
        self._hint = hint
        self._label = label
        self._required = required
        self._default = default

    def get_default(self):
        return self._default

    def get(self):
        return self._value

    def set(self, value):
        if not isinstance(value, self._type):
            raise ValueError('Invalid value for this kind of property.')
        self._value = value

    def is_required(self):
        return self._required

    def validate(self, value):
        return isinstance(value, self._type)

