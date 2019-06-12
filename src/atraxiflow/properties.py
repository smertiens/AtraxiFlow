#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

class Property:

    def __init__(self, value=None, expected_type=str, default=None, required=False, label='', hint=''):
        self._value = value
        self._type = expected_type
        self._hint = hint
        self._label = label
        self._required = required
        self._default = default

    def get_default(self):
        return self._default

    def value(self):
        return self._value

    def set_value(self, value):
        if value is not None and not self.validate(value):
            raise ValueError('Invalid value "{}", expected {} for this kind of property.'.format(value, self._type))
        self._value = value

    def is_required(self) -> bool:
        return self._required

    def validate(self, value) -> bool:
        tp = self._type
        if not isinstance(tp, tuple):
            tp = (self._type,)

        return type(value) in tp

