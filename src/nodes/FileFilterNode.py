from nodes.ProcessorNode import *
from common.FSObject import FSObject
from common import DateTimeProcessor
import logging, re

'''
Filter format

[file_property, comparator, value]

file_property:
    filesize
    date_created
    date_modified

comparator: < > = <= >= !=
'''


class FileFilterNode(ProcessorNode):
    _known_properties = {
        'filter': {
            'label': "List of filters",
            'type': "list",
            'required': True,
            'hint': 'Filters all or given filesystem resources',
            'default': {}
        },
        'sources': {
            'label': "Sources",
            'type': "string",
            'required': False,
            'hint': 'A resource query',
            'default': 'FS:*'
        }
    }

    children = []
    properties = {}

    def getNodeClass(self):
        return 'FileFilterNode'

    def _filesizeValueToNumber(self, str_size):
        matches = re.match("(\d+) *([MKGT]*)", str_size.lstrip(" ").rstrip(" "))

        if matches is None:
            logging.log("Invalid filesize format: %s".format(str_size))
            return 0

        if matches.group(2) == "":
            # only number
            return int(matches.group(1))
        else:
            f = 1
            if matches.group(2) == "K":
                f = 1024
            elif matches.group(2) == "M":
                f = 1024 * 1024
            elif matches.group(2) == "G":
                f = 1024 * 1024 * 1024
            elif matches.group(2) == "T":
                f = 1024 * 1024 * 1024 * 1024
            else:
                logging.log("Invalid filesize format suffix: %s".format(matches.group(2)))

            return int(matches.group(1)) * f

    def _matchesFilter(self, fso, filter):
        """

        :type fso: FSObject
        """
        leftVal = None
        rightVal = None

        if filter[0] == "file_size":
            leftVal = fso.getFilesize()
            rightVal = self._filesizeValueToNumber(filter[2])
        elif filter[0] == "date_created":
            leftVal = fso.getCreated()
            rightVal = DateTimeProcessor.processString(filter[2])
        elif filter[0] == "date_modified":
            leftVal = fso.getLastModified()
            rightVal = DateTimeProcessor.processString(filter[2])

        #print (fso.getBasename(), ": ", leftVal, filter[1], rightVal)

        if filter[1] == "<":
            return leftVal < rightVal
        elif filter[1] == ">":
            return leftVal > rightVal
        elif filter[1] == "=":
            return leftVal == rightVal
        elif filter[1] == "<=":
            return leftVal <= rightVal
        elif filter[1] == ">=":
            return leftVal >= rightVal
        elif filter[1] == "!=":
            return leftVal != rightVal
        else:
            logging.error("Invalid operator: %s".format(filter[1]))
            return False

    def run(self, stream):
        self.mergeProperties()

        # filter FSObjects from every resource and filter them down
        objectsToRemove = {}

        for resource in stream.getResource(self.getProperty('sources')):
            objectsToRemove[resource] = []

            # collect objects that do not match the criteria
            for filter in self.getProperty("filter"):
                for fso in resource.getData():
                    if not self._matchesFilter(fso, filter):
                        objectsToRemove[resource].append(fso)

        for res, objs in objectsToRemove.items():
            for o in objs:
                res.removeData(o)

        return True
