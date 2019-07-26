#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


def version_str_to_int(ver: str) -> int:
    maj, min, rev = ver.split('.')
    return maj * 100 + min * 10 + rev
