#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from common.filesystem import FSObject
import importlib.util
import logging



def check_environment():
    MAJ_VER_REQUIRED = 5
    MIN_VER_REQUIRED = 4

    spec = importlib.util.find_spec('PIL')

    if spec is None:
        logging.error(
            "You need to install the Pillow image library to use the ImageNodes. You can install it using pip:\n\n" + \
            "\tpip install Pillow\n\n" + \
            "In case you have PIL installed, you will need to uninstall it first before installing Pillow.")
        return False

    import PIL
    version = PIL.__version__.split('.')
    msg = "You need at least Pillow version 5.4 to use the ImageNodes. You can install/update Pillow using pip."

    if int(version[0]) < MAJ_VER_REQUIRED:
        logging.error(msg)
        return False
    if (int(version[1]) <MIN_VER_REQUIRED):
        logging.error(msg)
        return False

    return True

class ImageObject:

    def __init__(self, obj = None):

        self.src = None
        self.type = None
        self.img_object = None
        self._valid = False

        if obj is not None:
            if isinstance(obj, FSObject):
                self.src = obj
            elif type(obj) == str:
                self.src = FSObject(obj)
            else:
                logging.error('Cannot create an ImageObject from {0}', obj)
                self._valid = False

        if check_environment():
            from PIL import Image

            if self.src is not None:
                # try to load file
                try:
                    self.img_object = Image.open(self.src.getAbsolutePath())
                    self._valid = True
                except IOError:
                    self._valid = False
            else:
                self.img_object = Image()
                self._valid = True

    def width(self):
        if self._valid:
            return self.img_object.size[0]

    def height(self):
        if self._valid:
            return self.img_object.size[1]

    def is_valid(self):
        return self._valid

    def get_src(self):
        return self.src

    def get_type(self):
        return self.type

    def get_image_object(self):
        return self.img_object

    def set_src(self, src):
        self.src = src

    def set_type(self, imgtype):
        self.type = type

    def set_image_object(self, obj):
        self.img_object = obj





