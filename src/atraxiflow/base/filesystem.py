#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import os, glob
import re
import shutil
from pathlib import Path

from atraxiflow.base.resources import FilesystemResource
from atraxiflow.core import *
from atraxiflow.data import DatetimeProcessor, StringValueProcessor
from atraxiflow.exceptions import FilesystemException
from atraxiflow.properties import *
from atraxiflow.base import assets
from atraxiflow.creator.widgets import AxListWidget

from PySide2 import QtWidgets, QtCore, QtGui


class LoadFilesNode(Node):
    """
    @Name: Get files and folder
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

    def apply_ui_data(self):
        self.property('paths').set_value(self.list_widget.get_item_list())

    def add_path(self, lst: AxListWidget, mode='files'):
        path = ''

        if mode == 'text':
            text = QtWidgets.QInputDialog.getText(lst, 'Add path', 'Enter a path, you may use wildcards (*)',
                                                  QtWidgets.QLineEdit.Normal)

            if text[1]:
                path = [text[0]]

        else:
            dlg = QtWidgets.QFileDialog()

            if mode == 'files':
                dlg.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
            elif mode == 'folder':
                dlg.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

            dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
            if not dlg.exec_():
                return

            path = dlg.selectedFiles()

        self.list_widget.add_items(path)

    def get_ui(self):
        self.list_widget = AxListWidget()
        action_add_files = QtWidgets.QAction('+', self.list_widget.get_toolbar())
        action_add_files.connect(QtCore.SIGNAL('triggered()'), lambda lst=self.list_widget: self.add_path(lst, 'file'))
        action_add_files.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-file-50.png')))

        action_add_folder = QtWidgets.QAction('+F', self.list_widget.get_toolbar())
        action_add_folder.connect(QtCore.SIGNAL('triggered()'),
                                  lambda lst=self.list_widget: self.add_path(lst, 'folder'))
        action_add_folder.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-folder-50.png')))

        action_add_string = QtWidgets.QAction('+T', self.list_widget.get_toolbar())
        action_add_string.connect(QtCore.SIGNAL('triggered()'), lambda lst=self.list_widget: self.add_path(lst, 'text'))
        action_add_string.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-text-50.png')))

        self.list_widget.add_toolbar_action(action_add_files)
        self.list_widget.add_toolbar_action(action_add_folder)
        self.list_widget.add_toolbar_action(action_add_string)

        return self.list_widget


class FileFilterNode(Node):
    '''
    @Name: Filter files and folders

    Filter format

    [file_property, comparator, value]

    file_property:
        filesize
        date_created
        date_modified

    comparator: < > = <= >= !=
    '''

    def __init__(self, properties: dict = None):
        node_properties = {
            'filter': Property(expected_type=list, required=True, hint='Filters filesystem resources')
        }
        super().__init__(node_properties, properties)

    @staticmethod
    def get_name() -> str:
        return 'Filter files and folders'

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
                             hint='The destination on the filesystem to copy the source to'),
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


class FSRenameNode(Node):

    def __init__(self, properties: dict = None):
        node_properties = {
            'name': Property(expected_type=str, required=False, label='Target name',
                             hint='A string to rename the given files to', default=''),
            'replace': Property(expected_type=dict, required=False, default=None, label='Replace',
                                hint='A list of strings to replace. The key can be a compiled regular expression.'),
            'dry': Property(expected_type=bool, required=False, default=False, label='Dry run',
                            hint='If true no files/folders will be renamed, only a message in the log will be created')
        }
        super().__init__(node_properties, properties)

    def show_add_replace_dialog(self):
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle('Add string to replace')
        dlg.setLayout(QtWidgets.QVBoxLayout())

        form_layout = QtWidgets.QFormLayout()
        line_search = QtWidgets.QLineEdit()
        line_replace = QtWidgets.QLineEdit()

        form_layout.addRow('Search', line_search)
        form_layout.addRow('Replace', line_replace)
        btn_box = QtWidgets.QDialogButtonBox()
        btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.connect(QtCore.SIGNAL('accepted()'), dlg.accept)
        btn_box.connect(QtCore.SIGNAL('rejected()'), dlg.reject)
        dlg.layout().addLayout(form_layout)
        dlg.layout().addWidget(btn_box)

        result = dlg.exec_()

        if result == QtWidgets.QDialog.Accepted:
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, {line_search.text(), line_replace.text()})
            item.setText('{} -> {}'.format(line_search.text(), line_replace.text()))
            self.replace_list.add_item(item)

    def get_ui(self) -> QtWidgets.QWidget:

        def toggle_children(parent: QtWidgets.QWidget, state: bool):
            for child in parent.children():
                if isinstance(child, QtWidgets.QWidget):
                    child.setEnabled(state)

        def append_to_rename(txt: str):
            self.line_target_name.setText(self.line_target_name.text() + txt)

        widget = QtWidgets.QWidget()
        widget.setLayout(QtWidgets.QVBoxLayout())

        variables = {
            'File basename': '{file.basename}',
            'File extension': '{file.extension}',
            'File path': '{file.path}',
        }

        # Rename
        self.group_rename = QtWidgets.QGroupBox()
        self.group_rename.setTitle('Rename')
        self.group_rename.setCheckable(True)
        self.group_rename.setChecked(True)
        self.group_rename.connect(QtCore.SIGNAL('toggled(bool)'), lambda on: toggle_children(self.group_rename, on))
        self.group_rename.setLayout(QtWidgets.QVBoxLayout())

        ctx_target_name = QtWidgets.QMenu()
        for lbl, var in variables.items():
            action  = QtWidgets.QAction(ctx_target_name)
            action.setText(lbl)
            action.connect(QtCore.SIGNAL('triggered()'), lambda var=var: append_to_rename(var))
            ctx_target_name.addAction(action)

        self.line_target_name = QtWidgets.QLineEdit()
        self.line_target_name.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.line_target_name.connect(QtCore.SIGNAL('customContextMenuRequested(QPoint)'),
                                      lambda pos: ctx_target_name.exec_(self.line_target_name.mapToGlobal(pos)))


        rename_text = QtWidgets.QLabel('The new name will be applied to the whole path (so if you change the ' + \
                                       'directory part <strong>the files will be moved</strong>). There are a number ' + \
                                       'of variables available, take a look at the context menu for a list.')
        rename_text.setWordWrap(True)
        self.group_rename.layout().addWidget(rename_text)
        self.group_rename.layout().addWidget(self.line_target_name)

        # Replace
        self.group_replace = QtWidgets.QGroupBox()
        self.group_replace.setTitle('Replace')
        self.group_replace.setCheckable(True)
        self.group_replace.setChecked(False)
        self.group_replace.connect(QtCore.SIGNAL('toggled(bool)'), lambda on: toggle_children(self.group_replace, on))
        self.group_replace.setLayout(QtWidgets.QVBoxLayout())

        self.replace_list = AxListWidget()
        self.replace_list.layout().setContentsMargins(0, 0, 0, 0)
        action_add = QtWidgets.QAction('+T', self.replace_list.get_toolbar())
        action_add.connect(QtCore.SIGNAL('triggered()'), self.show_add_replace_dialog)
        action_add.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-text-50.png')))
        self.replace_list.add_toolbar_action(action_add)
        self.group_replace.layout().addWidget(self.replace_list)
        toggle_children(self.replace_list, False)

        self.check_dry = QtWidgets.QCheckBox()
        self.check_dry.setText('Dry run')

        widget.layout().addWidget(self.group_rename)
        widget.layout().addWidget(self.group_replace)
        widget.layout().addWidget(self.check_dry)

        return widget

    def apply_ui_data(self):

        if self.group_rename.isChecked():
            self.property('name').set_value(self.line_target_name.text())

        if self.group_replace.isChecked():

            repl_list = {}
            for n in range(0, self.replace_list.get_list().count()):
                item = self.replace_list.get_list().item(n)
                data = item.data(QtCore.Qt.UserRole)
                print(data, type(data))
                assert isinstance(data, dict)

                repl_list += data

            self.property('replace').set_value(repl_list)

        self.property('dry').set_value(self.check_dry.isChecked())

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
