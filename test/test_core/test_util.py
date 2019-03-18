#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import pytest

from atraxiflow.core.exceptions import *
from atraxiflow.core.util import *


def test_find_in_dict_by_path():
    d = {
        'hello': {
            'world': 123
        },
        'foo': {
            'bar': {
                'even': 'deeper'
            }
        }
    }

    assert 123 == dict_read_from_path(d, 'hello.world')
    assert 'deeper' == dict_read_from_path(d, 'foo.bar.even')
    assert {'world': 123} == dict_read_from_path(d, 'hello')

    with pytest.raises(ValueException):
        dict_read_from_path(d, 'hello.adasdada')
