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

        if obj is not None:
            if type(obj) == FSObject:
                self.src = FSObject
            elif type(obj) == str:
                self.src = FSObject(obj)

    def getSrc(self):
        return self.src

    def getType(self):
        return self.type

    def getImageObject(self):
        return self.img_object

    def setSrc(self, src):
        self.src = src

    def setType(self, imgtype):
        self.type = type

    def setImageObject(self, obj):
        self.img_object = obj





