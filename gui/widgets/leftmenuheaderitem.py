import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from gui import LEFT_MENU_APPREQUEST_TYPE, ADD_APP_REQUEST_PAGE, LEFT_MENU_SUBMISSION_TYPE, LEFT_MENU_REVIEW_TYPE


class LeftMenuHeaderItem(QWidget):

    def __init__(self, parent, type):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('gui', 'qt_resources', 'left_menu_header.ui'), self)

        self.type = type
        if self.type == LEFT_MENU_SUBMISSION_TYPE or self.type == LEFT_MENU_REVIEW_TYPE:
            self.new_button.hide()

        self.new_button.clicked.connect(self.on_new_button_clicked)

    def on_new_button_clicked(self):
        if self.type == LEFT_MENU_APPREQUEST_TYPE:
            self.window().stackedWidget.setCurrentIndex(ADD_APP_REQUEST_PAGE)
