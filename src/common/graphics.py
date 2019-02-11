from common.filesystem import FSObject

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





