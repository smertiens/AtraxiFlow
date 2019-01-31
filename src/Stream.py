class Stream:

    resources = []

    def addResource(self, res):
        self.resources.append(res)
    
    def removeResource(self, index):
        self.resources.pop(index)

    def getResources(self, type = ''):
        if (type == ''):
            return self.resources
        else:
            result = []

            for res in self.resources:
                if (res.type == type):
                    result.append(res)
            
            return result

