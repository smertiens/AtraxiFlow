#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from typing import Any, Dict

__all__ = ['Property']


class Property:
    """
    This class represents a single node property
    """

    def __init__(self, value=None, expected_type=str, default=None, required=False, label='', hint='',
                 display_options={}):
        """

        :param Any value: The value of the property
        :param type expected_type: The expected python type (e.g. str or bool)
        :param Any default: A default value
        :param bool required: True if the property is required to be able to run the node
        :param str label: The label shown in Creator for this property
        :param str hint: Some additional information on this property (usually shown in Creator as tooltip)
        :param dict display_options: Display options (type-specific)
        """
        if not isinstance(expected_type, tuple):
            expected_type = (expected_type,)

        self._value = value
        self._type = expected_type
        self._hint = hint
        self._label = label
        self._required = required
        self._default = default
        self._display_options = display_options

    def get_display_options(self) -> Dict[str, Any]:
        return self._display_options

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
        if value is not None and not self.validate(value) and not isinstance(value, MissingRequiredValue):
            raise ValueError('Invalid value "{}", expected {} for this kind of property.'.format(value, self._type))
        self._value = value

    def is_required(self) -> bool:
        return self._required

    def validate(self, value) -> bool:
        return type(value) in self._type


class MissingRequiredValue:
    """
    Dummy value that is used as value for required properties if they have no value set
    """
    pass
