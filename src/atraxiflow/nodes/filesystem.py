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
from atraxiflow.core.data import StringValueProcessor
from atraxiflow.core.exceptions import *
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
                'list_item': [
                    {
                        'name': 'prop',
                        'label': 'Property',
                        'type': 'combobox',
                        'value': ['filesize', 'date_created', 'date_modified']
                    },
                    {
                        'name': 'comp',
                        'label': 'Comparator',
                        'type': 'combobox',
                        'value': ['=', '<', '>', '<=', '>=', '!=']
                    },
                    {
                        'name': 'value',
                        'label': 'Value',
                        'type': 'text'
                    }
                ],
                'list_item_formatter': self.format_list_item,
                'required': True,
                'hint': 'Filters all or given filesystem resources',
                'default': {}
            },
            'sources': {
                'label': "Sources",
                'type': "resource_query",
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

    def format_list_item(self, format, data):
        if format == 'list':
            return '{0} {1} {2}'.format(data['prop'], data['comp'], data['value'])
        elif format == 'store':
            return data

    def _filesize_value_to_number(self, str_size):
        matches = re.match(r"(\d+) *([MKGT]*)", str_size.lstrip(" ").rstrip(" "))

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
        left_val = None
        right_val = None

        if filter[0] == "file_size":
            left_val = fso.getFilesize()
            right_val = self._filesize_value_to_number(filter[2])
        elif filter[0] == "date_created":
            left_val = fso.getCreated()
            right_val = DatetimeProcessor.processString(filter[2])
        elif filter[0] == "date_modified":
            left_val = fso.getLastModified()
            right_val = DatetimeProcessor.processString(filter[2])
        elif filter[0] == "type":
            left_val = 'folder' if fso.isFolder() else 'file'
            print(fso, left_val)
            right_val = filter[2]

            if filter[1] != '=':
                filter[1] = '='
                logging.warning('Filter "type" only supports comparison "equal" (=)')

        elif filter[0] == 'filename':

            right_val = filter[2]
            if filter[1] == 'contains':
                return fso.getFilename().find(right_val) > -1
            elif filter[1] == 'startswith':
                return fso.getFilename().startswith(right_val)
            elif filter[1] == 'endswith':
                return fso.getFilename().endswith(right_val)
            elif filter[1] == 'matches':
                if type(right_val) != type(re.compile('')):
                    logging.error('Value to compare needs to be a compiled regex when using "matches" operator.')
                    raise ExecutionException('Cannot continue due to previous errors. See log for details.')
                return right_val.match(fso.getFilename())
            else:
                logging.error(
                    'Filter "file_name" only supports operators: contain, startswith, endswith, matches (regex).')
                raise ExecutionException('Cannot continue due to previous errors. See log for details.')

        elif filter[0] == 'filedir':

            right_val = filter[2]
            if filter[1] == 'contains':
                return fso.getDirectory().find(right_val) > -1
            elif filter[1] == 'startswith':
                return fso.getDirectory().startswith(right_val)
            elif filter[1] == 'endswith':
                return fso.getDirectory().endswith(right_val)
            elif filter[1] == 'matches':
                if type(right_val) != type(re.compile('')):
                    logging.error('Value to compare needs to be a compiled regex when using "matches" operator.')
                    raise ExecutionException('Cannot continue due to previous errors. See log for details.')
                return right_val.match(fso.getDirectory())
            else:
                logging.error(
                    'Filter "file_name" only supports operators: contain, startswith, endswith, matches (regex).')
                raise ExecutionException('Cannot continue due to previous errors. See log for details.')

        if filter[1] == "<":
            return left_val < right_val
        elif filter[1] == ">":
            return left_val > right_val
        elif filter[1] == "=":
            return left_val == right_val
        elif filter[1] == "<=":
            return left_val <= right_val
        elif filter[1] == ">=":
            return left_val >= right_val
        elif filter[1] == "!=":
            return left_val != right_val
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


class FilesystemResource(Resource):
    """
    Provides access to the filesysmtem.
    """

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

        self._stream = None
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

        src = self.parse_string(self._stream, self.get_property("src"))
        items = glob.glob(src)
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
                'label': 'Create missing folders',
                'type': "bool",
                'required': False,
                'hint': 'Creates the destination path if it is missing',
                'default': True
            },
            'sources': {
                'label': 'Sources',
                'type': "resource_query",
                'required': False,
                'hint': 'Resource query for FilesystemResources',
                'default': 'FS:*'
            }
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def _do_copy(self, src, dest):
        # check if src and dest exist
        src_p = Path(src)
        dest_p = Path(dest)

        if not src_p.exists():
            logging.error("Source does not exist")
            raise FilesystemException('Source does not exist.')

        if src_p.is_file():
            if not dest_p.exists() and self.get_property("create_if_missing") is not True:
                logging.error("Destination does not exist and create_if_missing is False.")
                raise FilesystemException('Destination does not exist.')

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

        resources = stream.get_resources(self.get_property('sources'))

        for res in resources:
            dest = self.parse_string(stream, self.get_property('dest'))

            for src in res.get_data():

                if self._do_copy(src.getAbsolutePath(), dest) is not True:
                    return False

        return True


class FSRenameNode(ProcessorNode):

    def __init__(self, name="", props=None):
        self._known_properties = {
            'name': {
                'label': 'Target name',
                'type': "string",
                'required': False,
                'hint': 'A string to rename the given files to',
                'default': None
            },
            'replace': {
                'label': 'Replacements',
                'type': "list(string)",
                'required': False,
                'hint': 'A list of strings to replace. The key can be a compiled regular expression.',
                'default': None
            },
            'sources': {
                'label': 'Sources',
                'type': "resource_query",
                'required': False,
                'hint': 'Resource query for FilesystemResources',
                'default': 'FS:*'
            }
        }

        self._listeners = {}
        self.name, self.properties = self.get_properties_from_args(name, props)

    def run(self, stream):
        if not self.check_properties():
            logging.error("Cannot proceed because of previous errors")
            return False

        resources = stream.get_resources(self.get_property('sources'))

        for res in resources:
            if not isinstance(res, FilesystemResource):
                logging.error("Expected FilesystemResource, got {0}".format(type(res)))
                return False

            new_data = []
            for fso in res.get_data():

                edited_fso = fso
                new_name = fso.getAbsolutePath()

                if self.get_property('name') is not None:
                    svp = StringValueProcessor(stream)
                    svp.add_variable('file.basename', fso.getBasename())
                    svp.add_variable('file.extension', fso.getExtension())
                    svp.add_variable('file.path', fso.getDirectory())

                    new_name = svp.parse(self.get_property('name'))

                if self.get_property('replace') is not None:
                    for key, val in self.get_property('replace').items():

                        # since py > 3.7 returns 're.Pattern' as result of re.compile and
                        # other versions _sre.SRE_PATTERN, we use a little workaround here instead of using the actual object
                        if isinstance(key, type(re.compile(''))):
                            new_name = key.sub(val, new_name)
                        else:
                            new_name = new_name.replace(key, val)

                os.rename(fso.getAbsolutePath(), new_name)
                logging.debug("Renamed {0} to {1}".format(fso.getAbsolutePath(), new_name))

                # update object
                edited_fso = FSObject(new_name)

                new_data.append(edited_fso)
                res.update_data(new_data)

        return True
