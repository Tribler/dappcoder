import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from gui import LEFT_MENU_APPREQUEST_TYPE


class LeftMenuItem(QWidget):

    def __init__(self, parent, type, data_dict):
        QWidget.__init__(self, parent)
        self.type = type
        self.data_dict = data_dict
        uic.loadUi(os.path.join('qt_resources', 'left_menu_item.ui'), self)

        if self.type == LEFT_MENU_APPREQUEST_TYPE:
            self.name_label.setText(self.data_dict['name'])