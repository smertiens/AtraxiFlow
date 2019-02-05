from resources.Resource import *

class TextResource(Resource):

    def getPrefix(self):
        return 'Text'

    def setText(self, text):
        self.setProperty('text', text)

    def toString(self):
        return self.getProperty('text')

