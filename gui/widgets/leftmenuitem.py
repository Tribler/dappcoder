import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from gui import LEFT_MENU_APPREQUEST_TYPE, LEFT_MENU_SUBMISSION_TYPE, LEFT_MENU_REVIEW_TYPE


class LeftMenuItem(QWidget):

    def __init__(self, parent, type, data_dict):
        QWidget.__init__(self, parent)
        self.type = type
        self.data_dict = data_dict
        uic.loadUi(os.path.join('qt_resources', 'left_menu_item.ui'), self)

        if self.type == LEFT_MENU_APPREQUEST_TYPE:
            self.name_label.setText(self.data_dict['name'])
        elif self.type == LEFT_MENU_SUBMISSION_TYPE:
            self.name_label.setText(self.data_dict['project_name'])
            self.detail_label.setText("%d/%d reviews" % (self.data_dict['num_reviews'], self.data_dict['min_reviews']))
        elif self.type == LEFT_MENU_REVIEW_TYPE:
            self.name_label.setText(self.data_dict['project_name'])
            self.detail_label.setText("")
            self.status_button.hide()
