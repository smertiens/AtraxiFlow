#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from atraxiflow.core.exceptions import *

def is_iterable(obj):
    return isinstance(obj, dict) or isinstance(obj, list)


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
