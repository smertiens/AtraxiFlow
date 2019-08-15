#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


def version_str_to_int(ver: str) -> int:
    maj, min, rev = ver.split('.')
    return maj * 100 + min * 10 + rev


def version_tuple_to_int(ver: tuple) -> int:
    maj, min, rev = ver[0], ver[1], ver[2]
    return maj * 100 + min * 10 + rev


def version_tuple_to_str(ver: tuple) -> str:
    maj, min, rev = ver[0], ver[1], ver[2]
    return '{}.{}.{}'.format(maj, min, rev)
