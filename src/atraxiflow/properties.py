#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from typing import Any

class Property:

    def __init__(self, value=None, expected_type=str, default=None, required=False, label='', hint=''):
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)

        self._value = value
        self._type = expected_type
        self._hint = hint
        self._label = label
        self._required = required
        self._default = default

    def get_default(self) -> Any:
        return self._default

    def get_label(self) -> str:
        return self._label

    def get_hint(self) -> str:
        return self._hint

    def get_expected_type(self) -> Any:
        return self._type

    def value(self) -> Any:
        return self._value

    def set_value(self, value):
        if value is not None and not self.validate(value):
            raise ValueError('Invalid value "{}", expected {} for this kind of property.'.format(value, self._type))
        self._value = value

    def is_required(self) -> bool:
        return self._required

    def validate(self, value) -> bool:
        return type(value) in self._type

