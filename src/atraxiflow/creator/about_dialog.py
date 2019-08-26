#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#
from PySide2 import QtWidgets, QtCore
from atraxiflow import __version__

class AboutDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(QtWidgets.QVBoxLayout())

        heading = QtWidgets.QLabel('AtraxiFlow')
        heading.setStyleSheet('font-weight:bold; font-size: 20px;')
        self.layout().addWidget(heading)

        main1 = QtWidgets.QLabel(
            'Version: %s<br>' % __version__ +
            'Copyright (c) 2019 Sean Mertiens<br>' +
            'Icons by the wonderful folks at <a href="https://icons8.com/icons">Icons8</a>\n'
        )
        main1.setTextFormat(QtCore.Qt.RichText)
        main1.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        main1.setOpenExternalLinks(True)
        self.layout().addWidget(main1)

        license = QtWidgets.QLabel(
            '<p>This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero ' +
            'General Public License as published by the Free Software Foundation, either version 3 of the License, or ' +
            '(at your option) any later version.</p>' +

            '<p>This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the ' +
            'implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.</p>' +

            '<p>You should have received a copy of the GNU Affero General Public License along with this program.  If not, ' +
            'see <a href="https://www.gnu.org/licenses/">https://www.gnu.org/licenses/</a>.</p>'
        )
        license.setTextFormat(QtCore.Qt.RichText)
        license.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        license.setOpenExternalLinks(True)
        license.setWordWrap(True)
        self.layout().addWidget(license)

        buttons = QtWidgets.QDialogButtonBox()
        buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        buttons.connect(QtCore.SIGNAL('rejected()'), self.reject)
        self.layout().addWidget(buttons)
