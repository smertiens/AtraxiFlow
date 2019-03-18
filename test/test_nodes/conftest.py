#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

import importlib
import os


def pytest_ignore_collect(path, config):
    fname = os.path.basename(str(path))

    mod_pyside = importlib.util.find_spec('PySide2')
    mod_pytestqt = importlib.util.find_spec('pytestqt')

    if (not mod_pyside or not mod_pytestqt) and (fname.startswith('test_gui')):
        return True
    else:
        return False
