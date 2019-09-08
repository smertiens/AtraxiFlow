#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
import glob
import os
import re
import shutil
from pathlib import Path

from PySide2 import QtWidgets, QtCore, QtGui

from atraxiflow.base import assets
from atraxiflow.base.resources import FilesystemResource
from atraxiflow.core import *
from atraxiflow.creator.widgets import AxListWidget, AxNodeWidget
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

    def apply_ui_data(self):
        self.property('paths').set_value(self.list_widget.get_item_list())

    def load_ui_data(self):
        if isinstance(self.property('paths').value(), MissingRequiredValue):
            return

        for item in self.property('paths').value():
            self.list_widget.get_list().addItem(item)

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

    def get_ui(self, node_widget: AxNodeWidget) -> QtWidgets.QWidget:
        self.list_widget = AxListWidget()
        action_add_files = QtWidgets.QAction('Add file', self.list_widget.get_toolbar())
        action_add_files.connect(QtCore.SIGNAL('triggered()'), lambda lst=self.list_widget: self.add_path(lst, 'file'))
        action_add_files.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-file-50.png')))

        action_add_folder = QtWidgets.QAction('Add folder', self.list_widget.get_toolbar())
        action_add_folder.connect(QtCore.SIGNAL('triggered()'),
                                  lambda lst=self.list_widget: self.add_path(lst, 'folder'))
        action_add_folder.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-folder-50.png')))

        action_add_string = QtWidgets.QAction('Add path pattern', self.list_widget.get_toolbar())
        action_add_string.connect(QtCore.SIGNAL('triggered()'), lambda lst=self.list_widget: self.add_path(lst, 'text'))
        action_add_string.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-text-50.png')))

        self.list_widget.add_toolbar_action(action_add_files)
        self.list_widget.add_toolbar_action(action_add_folder)
        self.list_widget.add_toolbar_action(action_add_string)
        self.list_widget.list_changed.connect(node_widget.modified)

        return self.list_widget


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

    def show_add_condition_dialog(self, condition_class=''):
        dlg = QtWidgets.QDialog()
        dlg.setWindowTitle('Add new condition')
        dlg.setLayout(QtWidgets.QVBoxLayout())

        h_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel()
        h_layout.addWidget(label)
        combo_operator = QtWidgets.QComboBox()
        combo_operator.setEditable(False)
        h_layout.addWidget(combo_operator)

        operator_map = {}

        if condition_class in ('filename', 'dir'):
            operator_map = {
                'contains': 'contains',
                'starts with': 'startswith',
                'ends with': 'endswith',
                'matches (RegEx)': 'matches'
            }

            label.setText('Filename' if condition_class == 'filename' else 'Directory name')
            combo_operator.addItems(list(operator_map.keys()))
            control = QtWidgets.QLineEdit()
            h_layout.addWidget(control)

        elif condition_class == 'type':
            label.setText('Path is a ')
            control = QtWidgets.QComboBox()
            control.setEditable(False)
            control.addItems(['file', 'folder'])
            h_layout.addWidget(control)
            h_layout.removeWidget(combo_operator)

        elif condition_class in ('created', 'modified'):
            operator_map = {
                'less than': '<',
                'more than': '>',
                'equals': '=',
                'less or equal': '<=',
                'more or equal': '>=',
                'not': '!='
            }

            label.setText('Date created is' if condition_class == 'created' else 'Date modified is')
            combo_operator.addItems(list(operator_map.keys()))
            control = QtWidgets.QComboBox()
            control.setEditable(True)
            control.addItems(['today', 'yesterday', 'tomorrow'])
            control.setCurrentText('')
            h_layout.addWidget(control)

        elif condition_class == 'size':
            operator_map = {
                'less than': '<',
                'more than': '>',
                'equals': '=',
                'less or equal': '<=',
                'more or equal': '>=',
                'not': '!='
            }

            unit_map = {
                'Bytes': '',
                'Kilobytes': 'K',
                'Megabytes': 'M',
                'Gigabytes': 'G',
                'Terabytes': 'T'
            }

            label.setText('Filesize is')
            combo_operator.addItems(list(operator_map.keys()))
            control = QtWidgets.QSpinBox()
            control.setRange(1, 9999999)
            h_layout.addWidget(control)
            combo_unit = QtWidgets.QComboBox()
            combo_unit.setEditable(False)
            combo_unit.addItems(list(unit_map.keys()))
            h_layout.addWidget(combo_unit)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.connect(QtCore.SIGNAL('accepted()'), dlg.accept)
        button_box.connect(QtCore.SIGNAL('rejected()'), dlg.reject)

        dlg.layout().addLayout(h_layout)
        dlg.layout().addWidget(button_box)
        if dlg.exec_() == QtWidgets.QDialog.Rejected:
            return

        # Add list item
        if condition_class in ('filename', 'dir'):
            text = control.text()

            if combo_operator.currentText() == 'matches (RegEx)':
                text = re.compile(text)

            label = '%s %s "%s"' % ('Filename' if condition_class == 'filename' else 'Directory name',
                                    combo_operator.currentText(), control.text())
            data = ['filename' if condition_class == 'filename' else 'filedir',
                    operator_map[combo_operator.currentText()], control.text(), label]
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, data)
            item.setText(label)
            self.list_widget.add_item(item)

        elif condition_class == 'type':
            label = 'Path is a %s' % control.currentText()
            data = ['type', '=', control.currentText(), label]
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, data)
            item.setText(label)
            self.list_widget.add_item(item)

        elif condition_class in ('created', 'modified'):
            label = '%s %s "%s"' % ('Date created' if condition_class == 'created' else 'Date modified',
                                    combo_operator.currentText(), control.currentText())
            data = ['date_created' if condition_class == 'created' else 'date_modified', combo_operator.currentText(),
                    control.currentText(), label]
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, data)
            item.setText(label)
            self.list_widget.add_item(item)

        elif condition_class == 'size':
            label = 'File size %s %s %s' % (combo_operator.currentText(), control.text(), combo_unit.currentText())
            data = ['file_size', combo_operator.currentText(), control.text() + combo_unit.currentText(), label]
            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, data)
            item.setText(label)
            self.list_widget.add_item(item)

    def apply_ui_data(self):
        conditions = []
        for n in range(0, self.list_widget.get_list().count()):
            item = self.list_widget.get_list().item(n)
            conditions.append(item.data(QtCore.Qt.UserRole))

        self.property('filter').set_value(conditions)

    def load_ui_data(self):
        for data in self.property('filter').value():
            item = QtWidgets.QListWidgetItem(data[3])
            item.setData(QtCore.Qt.UserRole, data)
            self.list_widget.add_item(item)

    def get_ui(self, node_widget: AxNodeWidget) -> QtWidgets.QWidget:
        self.list_widget = AxListWidget(show_edit_button=False)
        self.list_widget.list_changed.connect(node_widget.modified)
        btn_add_cond = QtWidgets.QPushButton()
        btn_add_cond.setObjectName('ax_toolbar_pushbutton')
        mnu_cond = QtWidgets.QMenu(btn_add_cond)

        action_add_filename = QtWidgets.QAction('Filter by filename', mnu_cond)
        action_add_filename.connect(QtCore.SIGNAL('triggered()'), lambda: self.show_add_condition_dialog('filename'))
        action_add_dir = QtWidgets.QAction('Filter by directory', mnu_cond)
        action_add_dir.connect(QtCore.SIGNAL('triggered()'), lambda: self.show_add_condition_dialog('dir'))
        action_add_type = QtWidgets.QAction('Filter by file type', mnu_cond)
        action_add_type.connect(QtCore.SIGNAL('triggered()'), lambda: self.show_add_condition_dialog('type'))
        action_add_created = QtWidgets.QAction('Filter by date created', mnu_cond)
        action_add_created.connect(QtCore.SIGNAL('triggered()'), lambda: self.show_add_condition_dialog('created'))
        action_add_modified = QtWidgets.QAction('Filter by date modified', mnu_cond)
        action_add_modified.connect(QtCore.SIGNAL('triggered()'), lambda: self.show_add_condition_dialog('modified'))
        action_add_size = QtWidgets.QAction('Filter by file size', mnu_cond)
        action_add_size.connect(QtCore.SIGNAL('triggered()'), lambda: self.show_add_condition_dialog('size'))
        mnu_cond.addAction(action_add_filename)
        mnu_cond.addAction(action_add_dir)
        mnu_cond.addAction(action_add_type)
        mnu_cond.addAction(action_add_created)
        mnu_cond.addAction(action_add_modified)
        mnu_cond.addAction(action_add_size)

        btn_add_cond.setIconSize(QtCore.QSize(20, 20))
        btn_add_cond.setFlat(True)
        btn_add_cond.setMenu(mnu_cond)
        btn_add_cond.setIcon(QtGui.QIcon(assets.get_asset('icons8-add-file-50.png')))

        self.list_widget.add_toolbar_widget(btn_add_cond)

        return self.list_widget

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
            item.setData(QtCore.Qt.UserRole, [line_search.text(), line_replace.text()])
            item.setText('{} -> {}'.format(line_search.text(), line_replace.text()))
            self.replace_list.add_item(item)

    def get_ui(self, node_widget: AxNodeWidget) -> QtWidgets.QWidget:

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
            action = QtWidgets.QAction(ctx_target_name)
            action.setText(lbl)
            action.connect(QtCore.SIGNAL('triggered()'), lambda var=var: append_to_rename(var))
            ctx_target_name.addAction(action)

        self.line_target_name = QtWidgets.QLineEdit()
        self.line_target_name.connect(QtCore.SIGNAL('textChanged(QString)'), lambda s: node_widget.modified)
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

        self.replace_list = AxListWidget(show_edit_button=False)
        self.replace_list.list_changed.connect(node_widget.modified)
        self.replace_list.layout().setContentsMargins(0, 0, 0, 0)
        action_add = QtWidgets.QAction('Add replacement rule', self.replace_list.get_toolbar())
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
                assert isinstance(data, list)

                repl_list[data[0]] = data[1]

            self.property('replace').set_value(repl_list)

        self.property('dry').set_value(self.check_dry.isChecked())

    def load_ui_data(self):
        self.group_rename.setChecked(self.property('name').value() != '')
        self.group_replace.setChecked(len(self.property('replace').value()) > 0)
        self.check_dry.setChecked(self.property('dry').value())
        self.line_target_name.setText(self.property('name').value())

        for find, repl in self.property('replace').value().items():
            item = QtWidgets.QListWidgetItem()
            item.setText('%s -> %s' % (find, repl))
            item.setData(QtCore.Qt.UserRole, [find, repl])
            self.replace_list.add_item(item)

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
