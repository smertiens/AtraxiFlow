#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import os
import re
import shutil
from pathlib import Path

from atraxiflow.base.resources import FilesystemResource
from atraxiflow.core import *
from atraxiflow.data import DatetimeProcessor
from atraxiflow.exceptions import FilesystemException
from atraxiflow.properties import *


class LoadFilesNode(Node):

    def __init__(self, properties: dict = None):
        self.output = Container()
        self.properties = {
            'path': Property(expected_type=str, required=True)
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def run(self, ctx: WorkflowContext):
        self.output = Container(FilesystemResource(self.property('path').value()))


class FileFilterNode(Node):
    '''
    Filter format

    [file_property, comparator, value]

    file_property:
        filesize
        date_created
        date_modified

    comparator: < > = <= >= !=
    '''

    def __init__(self, properties: dict = None):
        self.output = Container()
        self.properties = {
            'filter': Property(expected_type=list, required=True, hint='Filters filesystem resources')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def _filesize_value_to_number(self, str_size):
        matches = re.match(r"(\d+) *([MKGT]*)", str_size.lstrip(" ").rstrip(" "))

        if matches is None:
            self.ctx.get_logger().log("Invalid filesize format: %s".format(str_size))
            return 0

        if matches.group(2) == "":
            # only number
            return int(matches.group(1))
        else:
            f = 1
            ext = matches.group(2).upper()
            if ext == "K":
                f = 1024
            elif ext == "M":
                f = 1024 * 1024
            elif ext == "G":
                f = 1024 * 1024 * 1024
            elif ext == "T":
                f = 1024 * 1024 * 1024 * 1024
            else:
                self.ctx.get_logger().log("Invalid filesize format suffix: %s".format(matches.group(2)))

            return int(matches.group(1)) * f

    def _matches_filter(self, fso, filter):
        """

        :type fso: FSObject
        """
        left_val = None
        right_val = None

        dtp = DatetimeProcessor()

        if filter[0] == "file_size":
            left_val = fso.getFilesize()
            right_val = self._filesize_value_to_number(filter[2])
        elif filter[0] == "date_created":
            left_val = fso.getCreated()
            right_val = dtp.process_string(filter[2])

            if dtp.get_range() == DatetimeProcessor.RANGE_DATE:
                left_val.replace(hour=0, minute=0, second=0, microsecond=0)
                right_val.replace(hour=0, minute=0, second=0, microsecond=0)
            elif dtp.get_range() == DatetimeProcessor.RANGE_DATETIME_SHORT:
                left_val.replace(second=0, microsecond=0)
                right_val.replace(second=0, microsecond=0)
            elif dtp.get_range() == DatetimeProcessor.RANGE_DATETIME_LONG:
                left_val.replace(microsecond=0)
                right_val.replace(microsecond=0)

        elif filter[0] == "date_modified":
            left_val = fso.getLastModified()
            right_val = dtp.process_string(filter[2])

            if dtp.get_range() == DatetimeProcessor.RANGE_DATE:
                left_val = left_val.replace(hour=0, minute=0, second=0, microsecond=0)
                right_val = right_val.replace(hour=0, minute=0, second=0, microsecond=0)
            elif dtp.get_range() == DatetimeProcessor.RANGE_DATETIME_SHORT:
                left_val = left_val.replace(second=0, microsecond=0)
                right_val = right_val.replace(second=0, microsecond=0)
            elif dtp.get_range() == DatetimeProcessor.RANGE_DATETIME_LONG:
                left_val = left_val.replace(microsecond=0)
                right_val = right_val.replace(microsecond=0)

        elif filter[0] == "type":
            left_val = 'folder' if fso.isFolder() else 'file'
            right_val = filter[2]

            if filter[1] != '=':
                filter[1] = '='
                self.ctx.get_logger().warning('Filter "type" only supports comparison "equal" (=)')

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
                    self.ctx.get_logger().error(
                        'Value to compare needs to be a compiled regex when using "matches" operator.')
                    raise Exception('Cannot continue due to previous errors. See log for details.')
                return right_val.match(fso.getFilename())
            else:
                self.ctx.get_logger().error(
                    'Filter "file_name" only supports operators: contain, startswith, endswith, matches (regex).')
                raise Exception('Cannot continue due to previous errors. See log for details.')

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
                    self.ctx.get_logger().error(
                        'Value to compare needs to be a compiled regex when using "matches" operator.')
                    raise Exception('Cannot continue due to previous errors. See log for details.')
                return right_val.match(fso.getDirectory())
            else:
                self.ctx.get_logger().error(
                    'Filter "file_name" only supports operators: contain, startswith, endswith, matches (regex).')
                raise Exception('Cannot continue due to previous errors. See log for details.')

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
            self.ctx.get_logger().error("Invalid operator: %s".format(filter[1]))
            return False

    def run(self, ctx: WorkflowContext):
        self.output = Container()
        self.ctx = ctx
        # filter FSObjects from every resource and filter them down

        for resource in self.get_input().find('atraxiflow.FilesystemResource'):
            objects_to_remove = set()  # set values are unique

            # collect objects that do not match the criteria
            for filter in self.property("filter").value():
                for fso in resource.get_value():

                    if not self._matches_filter(fso, filter):
                        objects_to_remove.add(fso)

            current_objects = set(resource.get_value())

            for obj in (current_objects - objects_to_remove):
                new_res = FilesystemResource(obj.getAbsolutePath())
                self.output.add(new_res)

        return True


class FSCopyNode(Node):

    def __init__(self, properties: dict = None):
        self.output = Container()
        self.properties = {
            'dest': Property(expected_type=str, required=True,
                             hint='The destination on the filesystem to copy the source to'),
            'create_if_missing': Property(expected_type=bool, required=False, label='Create missing folders',
                                          hint='Creates the destination path if it is missing', default=True),
            'dry': Property(expected_type=bool, required=False, default=False, label='Dry run',
                            hint='If true no files/folders will be renamed, only a message in the log will be created')
        }
        self.id = '%s.%s' % (self.__module__, self.__class__.__name__)
        self._input = None

        self.apply_properties(properties)

    def _do_copy(self, src, dest):
        # check if src and dest exist
        src_p = Path(src)
        dest_p = Path(dest)

        if not src_p.exists():
            self._ctx.get_logger().error("Source does not exist")
            raise FilesystemException('Source does not exist.')

        if src_p.is_file():
            if not dest_p.exists() and self.property("create_if_missing").value() is not True:
                self._ctx.get_logger().error("Destination does not exist and create_if_missing is False.")
                raise FilesystemException('Destination does not exist.')

            elif not dest_p.exists() and self.property("create_if_missing").value() is True:
                os.makedirs(str(dest_p.absolute()))

            self._ctx.get_logger().debug("Copying file: {0} -> {1}".format(src_p, dest_p))
            shutil.copy(str(src_p.absolute()), str(dest_p.absolute()))
            self.output.add(FilesystemResource(os.path.join(str(dest_p.absolute()), str(src_p.name))))

        elif src_p.is_dir():
            if dest_p.exists():
                self._ctx.get_logger().error("Destination directory already exists")
                return False

            self._ctx.get_logger().debug("Copying directory: {0} -> {1}".format(src_p, dest_p))
            shutil.copytree(str(src_p.absolute()), str(dest_p.absolute()))
            self.output.add(FilesystemResource(str(dest_p.absolute())))

        return True

    def run(self, ctx: WorkflowContext):
        self._ctx = ctx
        self.output = Container()

        resources = self.get_input().find('atraxiflow.FilesystemResource')

        if len(resources) == 0:
            ctx.get_logger().warning('No resources found for copying.')

        for res in resources:
            dest = ctx.process_str(self.property('dest').value())

            for src in res.get_value():
                if self.property('dry').value() is True:
                    ctx.get_logger().info("DRY RUN: Copy {0} -> {1}".format(src.getAbsolutePath(), dest))
                else:
                    if self._do_copy(src.getAbsolutePath(), dest) is not True:
                        return False

        return True
