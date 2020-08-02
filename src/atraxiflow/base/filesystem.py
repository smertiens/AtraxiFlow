#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import glob
import os, sys
import re
import shutil
from pathlib import Path

from atraxiflow.base import assets
from atraxiflow.base.resources import FilesystemResource
from atraxiflow.core import *
from atraxiflow.data import DatetimeProcessor, StringValueProcessor
from atraxiflow.exceptions import FilesystemException
from atraxiflow.properties import *


class LoadFilesNode(Node):
    """
    @Name: Get files and folders
    """

    def __init__(self, properties: dict = None):
        node_properties = {
            'paths': Property(expected_type=list, required=True)
        }
        super().__init__(node_properties, properties)
        self.list_widget = None

    @staticmethod
    def get_name() -> str:
        return 'Get files and folders'

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        self.output.clear()

        expanded_paths = []
        for path in self.property('paths').value():
            # resolve wildcards
            path_exp = glob.glob(path)

            for sub_path in path_exp:
                expanded_paths.append(os.path.realpath(sub_path))

        for path in expanded_paths:
            self.output.add(FilesystemResource(path))

class FileFilterNode(Node):
    """
    @Name: Filter files and folders
    """

    def __init__(self, properties: dict = None):
        node_properties = {
            'filter': Property(expected_type=list, required=True, hint='Filters filesystem resources')
        }
        super().__init__(node_properties, properties)

    def _filesize_value_to_number(self, str_size: str) -> int:
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

    def _matches_filter(self, fsres: FilesystemResource, filter: dict) -> bool:
        left_val = None
        right_val = None

        dtp = DatetimeProcessor()

        if filter[0] == "file_size":
            left_val = fsres.get_filesize()
            right_val = self._filesize_value_to_number(filter[2])

        elif filter[0] == "date_created":
            left_val = fsres.get_created()
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
            left_val = fsres.get_last_modified()
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
            left_val = 'folder' if fsres.is_folder() else 'file'
            right_val = filter[2]

            if filter[1] != '=':
                filter[1] = '='
                self.ctx.get_logger().warning('Filter "type" only supports comparison "equal" (=)')

        elif filter[0] == 'filename':

            right_val = filter[2]
            if filter[1] == 'contains':
                return fsres.get_filename().find(right_val) > -1
            elif filter[1] == 'startswith':
                return fsres.get_filename().startswith(right_val)
            elif filter[1] == 'endswith':
                return fsres.get_filename().endswith(right_val)
            elif filter[1] == 'matches':
                if type(right_val) != type(re.compile('')):
                    self.ctx.get_logger().error(
                        'Value to compare needs to be a compiled regex when using "matches" operator.')
                    raise Exception('Cannot continue due to previous errors. See log for details.')
                return right_val.match(fsres.get_filename())
            else:
                self.ctx.get_logger().error(
                    'Filter "file_name" only supports operators: contain, startswith, endswith, matches (regex).')
                raise Exception('Cannot continue due to previous errors. See log for details.')

        elif filter[0] == 'filedir':

            right_val = filter[2]
            if filter[1] == 'contains':
                return fsres.get_directory().find(right_val) > -1
            elif filter[1] == 'startswith':
                return fsres.get_directory().startswith(right_val)
            elif filter[1] == 'endswith':
                return fsres.get_directory().endswith(right_val)
            elif filter[1] == 'matches':
                if type(right_val) != type(re.compile('')):
                    self.ctx.get_logger().error(
                        'Value to compare needs to be a compiled regex when using "matches" operator.')
                    raise Exception('Cannot continue due to previous errors. See log for details.')
                return right_val.match(fsres.get_directory())
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
        super().run(ctx)
        self.output.clear()
        self.ctx = ctx

        for resource in self.get_input().find('atraxiflow.FilesystemResource'):
            passed = True

            for filter in self.property("filter").value():
                passed = passed and self._matches_filter(resource, filter)

            if passed:
                self.output.add(resource)

        return True


class FSCopyNode(Node):
    """
    @Name: Copy files and folders
    """

    def __init__(self, properties: dict = None):
        node_properties = {
            'dest': Property(expected_type=str, required=True, label='Destination',
                             hint='The destination on the filesystem to copy the source to',
                             display_options={'role': 'folder'}),
            'create_if_missing': Property(expected_type=bool, required=False, label='Create missing folders',
                                          hint='Creates the destination path if it is missing', default=True),
            'dry': Property(expected_type=bool, required=False, default=False, label='Dry run',
                            hint='If true no files/folders will be copied, only a message in the log will be created')
        }
        super().__init__(node_properties, properties)

    def _do_copy(self, src: str, dest: str) -> bool:
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

            # When trying to copy from a directory to another directory contained in the first one
            # an inifinte loop can occur. This is due to a bug introduced in Python 3.8.0, see here:
            # https://bugs.python.org/issue38688.
            # The bug is fixed in 3.8.1
            if sys.version_info.major == 3 and \
                sys.version_info.minor == 8 and \
                sys.version_info.micro == 0:

                self._ctx.get_logger().warn('Your Python version is 3.8.0. Trying to copy a directory tree in ' + 
                    'this version will cause an error (see here for details: https://bugs.python.org/issue38688. ' + 
                    'Please consider updating to Python 3.8.1 or greater.')
                self._ctx.get_logger().error('Skipping copy operation (see notice above).')
                return False
                
            shutil.copytree(str(src_p.absolute()), str(dest_p.absolute()))
            self.output.add(FilesystemResource(str(dest_p.absolute())))

        return True

    def run(self, ctx: WorkflowContext):
        super().run(ctx)
        self._ctx = ctx
        self.output.clear()

        resources = self.get_input().find('atraxiflow.FilesystemResource')

        if len(resources) == 0:
            ctx.get_logger().warning('No resources found for copying.')

        dest = ctx.process_str(self.property('dest').value())
        for res in resources:
            if self.property('dry').value() is True:
                ctx.get_logger().info("DRY RUN: Copy {0} -> {1}".format(res.get_absolute_path(), dest))
            else:
                if self._do_copy(res.get_absolute_path(), dest) is not True:
                    return False

        return True


class FSMoveNode(Node):
    """
    @Name: Move files
    """

    def __init__(self, properties=None):
        node_properties = {
            'dest': Property(expected_type=str, required=True, label='Destination',
                             hint='The directoy to move the files to',
                             display_options={'role': 'folder'}),
            'create_dirs': Property(expected_type=bool, required=False, label='Create destination directories',
                                    hint='Create missing destination paths', default=False),
            'dry': Property(expected_type=bool, required=False, label='Dry', hint='Simulate file operation',
                            default=False)
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

        # In case the node is run multiple times, we will empty the output container
        self.output.clear()

        if self.property('create_dirs').value() and not os.path.exists(self.property('dest').value()):
            ctx.get_logger().debug('Creating missing destination directory "%s"' % self.property('dest').value())
            os.makedirs(self.property('dest').value())

        resources = self.get_input().find('atraxiflow.FilesystemResource')
        for res in resources:
            assert isinstance(res, FilesystemResource)  # helps with autocompletion

            dest_name = os.path.join(self.property('dest').value(), res.get_filename())

            if self.property('dry').value():
                ctx.get_logger().debug('DRY RUN: Moving file "%s" -> "%s"' % (res.get_absolute_path(), dest_name))
            else:
                ctx.get_logger().debug('Moving file "%s" -> "%s"' % (res.get_absolute_path(), dest_name))
                os.rename(res.get_absolute_path(), dest_name)

            self.output.add(FilesystemResource(dest_name))

        return True


class FSRenameNode(Node):
    """
    @Name: Rename files and folders
    """

    def __init__(self, properties: dict = None):
        node_properties = {
            'name': Property(expected_type=str, required=False, label='Target name',
                             hint='A string to rename the given files to', default=''),
            'replace': Property(expected_type=dict, required=False, default={}, label='Replace',
                                hint='A list of strings to replace. The key can be a compiled regular expression.'),
            'dry': Property(expected_type=bool, required=False, default=False, label='Dry run',
                            hint='If true no files/folders will be renamed, only a message in the log will be created')
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

        self._ctx = ctx
        self.output = Container()

        resources = self.get_input().find('atraxiflow.FilesystemResource')

        for res in resources:
            assert isinstance(res, FilesystemResource)  # helps with autocompletion

            new_name = res.get_absolute_path()
            svp = StringValueProcessor(ctx)

            if self.property('name').value() != '':
                svp.add_variable('file.basename', res.get_basename())
                svp.add_variable('file.extension', res.get_extension())
                svp.add_variable('file.path', res.get_directory())

                new_name = svp.parse(self.property('name').value())

            if self.property('replace').value() is not None:
                for key, val in self.property('replace').value().items():

                    # since py > 3.7 returns 're.Pattern' as result of re.compile and
                    # other versions _sre.SRE_PATTERN, we use a little workaround here instead of using the actual
                    # object
                    if isinstance(key, type(re.compile(''))):
                        new_name = key.sub(svp.parse(val), new_name)
                    else:
                        new_name = new_name.replace(key, svp.parse(val))

            if self.property('dry').value() is True:
                ctx.get_logger().debug("DRY RUN: Rename {0} -> {1}".format(res.get_absolute_path(), new_name))
                self.output.add(FilesystemResource(new_name))
            else:
                os.rename(res.get_absolute_path(), new_name)
                self.output.add(FilesystemResource(new_name))
                ctx.get_logger().debug("Renamed {0} to {1}".format(res.get_absolute_path(), new_name))

        return True


class FSDeleteNode(Node):
    """
    @Name: Delete files
    """

    def __init__(self, properties=None):
        node_properties = {
            'del_nonempty_dirs': Property(expected_type=bool, required=False, label='Delete non-empty directories',
                                          default=False),
            'dry': Property(expected_type=bool, required=False, label='Dry', hint='Simulate file operation',
                            default=False)
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

        # In case the node is run multiple times, we will empty the output container
        self.output.clear()

        resources = self.get_input().find('atraxiflow.FilesystemResource')
        for res in resources:
            del_okay = False

            assert isinstance(res, FilesystemResource)  # helps with autocompletion

            if res.is_symlink():
                if self.property('dry').value():
                    ctx.get_logger().debug('DRY RUN: Deleting symlink "%s"' % res.get_absolute_path())
                    del_okay = True
                else:
                    ctx.get_logger().debug('Deleting symlink "%s"' % res.get_absolute_path())
                    os.unlink(res.get_absolute_path())
                    del_okay = True

            elif res.is_file():
                if self.property('dry').value():
                    ctx.get_logger().debug('DRY RUN: Deleting file "%s"' % res.get_absolute_path())
                    del_okay = True
                else:
                    ctx.get_logger().debug('Deleting file "%s"' % res.get_absolute_path())
                    os.unlink(res.get_absolute_path())
                    del_okay = True

            elif res.is_folder():
                if self.property('dry').value():
                    ctx.get_logger().debug('DRY RUN: Deleting directory "%s"' % res.get_absolute_path())
                    del_okay = True
                else:
                    try:
                        ctx.get_logger().debug('Deleting directory "%s"' % res.get_absolute_path())
                        os.rmdir(res.get_absolute_path())
                        del_okay = True

                    except OSError:
                        # might be a non-empty directory, try again if needed
                        if self.property('del_nonempty_dirs').value():
                            ctx.get_logger().debug('Directory is not empty. Deleting all contents.')
                            shutil.rmtree(res.get_absolute_path())
                            del_okay = True

                        else:
                            ctx.get_logger().warning(
                                'Could not delete directory "%s", might be not empty (see del_nonempty_dirs option)' %
                                res.get_absolute_path())

            if del_okay:
                self.output.add(FilesystemResource(res.get_absolute_path()))

        return True


class FSChangeCWDNode(Node):
    """
    @Name: Change current directory
    """

    def __init__(self, properties=None):
        node_properties = {
            'cwd': Property(expected_type=str, required=True, label='New working directory', display_options={'role':'folder'})
        }
        super().__init__(node_properties, properties)

    def run(self, ctx: WorkflowContext):
        super().run(ctx)

        # In case the node is run multiple times, we will empty the output container
        self.output.clear()

        if not os.path.exists(self.property('cwd').value()):
            ctx.get_logger().error('Invalid directory path: %s' % self.property('cwd').value())
            return False

        os.chdir(self.property('cwd').value())
        self.output.add(FilesystemResource(self.property('cwd').value()))

        return True
