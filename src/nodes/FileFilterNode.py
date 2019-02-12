#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from nodes.foundation import ProcessorNode
from common.filesystem import FSObject
from common.data import DatetimeProcessor
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


    def __init__(self, name="", props=None):
        self.name = name
        self._known_properties = {
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
        self.children = []
        self._listeners = {}

        if props:
            self.properties = props
        else:
            self.properties = {}

    def _filesize_value_to_number(self, str_size):
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

    def _matches_filter(self, fso, filter):
        """

        :type fso: FSObject
        """
        leftVal = None
        rightVal = None

        if filter[0] == "file_size":
            leftVal = fso.getFilesize()
            rightVal = self._filesize_value_to_number(filter[2])
        elif filter[0] == "date_created":
            leftVal = fso.getCreated()
            rightVal = DatetimeProcessor.processString(filter[2])
        elif filter[0] == "date_modified":
            leftVal = fso.getLastModified()
            rightVal = DatetimeProcessor.processString(filter[2])

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
        self.check_properties()

        # filter FSObjects from every resource and filter them down

        for resource in stream.get_resources(self.get_property('sources')):
            objects_to_remove = set() # set values are unique

            # collect objects that do not match the criteria
            for filter in self.get_property("filter"):
                for fso in resource.get_data():
                    if not self._matches_filter(fso, filter):
                        objects_to_remove.add(fso)

            current_objects = set(resource.get_data())
            resource.update_data(list( current_objects - objects_to_remove ))

        return True
