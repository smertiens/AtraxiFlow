#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#


import glob
import logging
import os
import re
import shutil
from pathlib import Path

from atraxiflow.core.data import DatetimeProcessor
from atraxiflow.core.filesystem import FSObject
from atraxiflow.core.properties import PropertyObject
from atraxiflow.nodes.foundation import ProcessorNode
from atraxiflow.nodes.foundation import Resource

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

        # print (fso.getBasename(), ": ", leftVal, filter[1], rightVal)

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
            objects_to_remove = set()  # set values are unique

            # collect objects that do not match the criteria
            for filter in self.get_property("filter"):
                for fso in resource.get_data():
                    if not self._matches_filter(fso, filter):
                        objects_to_remove.add(fso)

            current_objects = set(resource.get_data())
            resource.update_data(list(current_objects - objects_to_remove))

        return True


"""
Provides access to the filesysmtem.

Properties:
    src - a qualified a qualified path to a file folder, can include wildcards 
"""


class FilesystemResource(Resource):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'src': {
                'label': "Source",
                'type': "file",
                'required': True,
                'hint': 'A file or folder',
                'default': ''
            }
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

        # node specific
        self._fsobjects = []
        self._resolved = False

        # events
        self.add_listener(PropertyObject.EVENT_PROPERTY_CHANGED, self._ev_property_changed)
        self.add_listener(PropertyObject.EVENT_PROPERTIES_CHECKED, self._ev_properties_checked)

    def _ev_properties_checked(self, data):
        if data is True:
            self._resolve()

    def _ev_property_changed(self, data):
        if data == 'src':
            self._resolved = False
            self._resolve()

    def get_prefix(self):
        return 'FS'

    def _resolve(self):
        if self._resolved:
            return

        items = glob.glob(self.get_property("src"))
        self._fsobjects.clear()

        for item in items:
            self._fsobjects.append(FSObject(item))

        self._resolved = True

    def remove_data(self, obj):
        if obj not in self._fsobjects:
            logging.error("Cannot remove: {0}, not found in this resource".format(obj))
            return

        self._fsobjects.remove(obj)

    def get_data(self):
        self.check_properties()
        return self._fsobjects

    def update_data(self, data):
        if not isinstance(data, list):
            logging.error("Expected List, got {0}".format(type(data)))
            return

        self._fsobjects = data


# TODO: check what happens when trying to copy a directory inside its own subdirectory - led to infinite loop last time

class FSCopyNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'dest': {
                'label': "Destination folder",
                'type': "folder",
                'required': True,
                'hint': 'The destination on the filesystem to copy the source to',
                'default': ''
            },
            'create_if_missing': {
                'type': "bool",
                'required': False,
                'hint': 'Creates the destination path if it is missing',
                'default': True
            },
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def _do_copy(self, src, dest):
        # check if src and dest exist
        src_p = Path(src)
        dest_p = Path(dest)

        if not src_p.exists():
            logging.error("Source does not exist")
            return False

        if src_p.is_file():
            if not dest_p.exists() and self.get_property("create_if_missing") is not True:
                logging.error("Destination does not exist")
                return False
            elif not dest_p.exists() and self.get_property("create_if_missing") is True:
                os.makedirs(str(dest_p.absolute()))

            logging.info("Copying file {0} to {1}".format(src_p, dest_p))
            shutil.copy(str(src_p.absolute()), str(dest_p.absolute()))

        elif src_p.is_dir():
            if dest_p.exists():
                logging.error("Destination directory already exists")
                return False

            logging.info("Copying directory {0} to {1}".format(src_p, dest_p))
            shutil.copytree(str(src_p.absolute()), str(dest_p.absolute()))

        return True

    def run(self, stream):
        if not self.check_properties():
            logging.error("Cannot proceed because of previous errors")
            return False

        resources = stream.get_resources("FS:*")

        for res in resources:
            src = res.get_data()

            if len(src) > 1:
                logging.error("Received more than one FSObject. Please narrow down your src-filter.")
                return False

            src = src[0].getAbsolutePath()

            dest = self.get_property('dest')
            if self._do_copy(src, dest) is not True:
                return False

        return True
