#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
def is_iterable(obj):
    return isinstance(obj, dict) or isinstance(obj, list)
