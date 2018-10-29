import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class UserItem(QWidget):

    def __init__(self, parent, user_dict):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'user_item.ui'), self)

        self.user_dict = user_dict
        self.username_label.setText(self.user_dict['username'])