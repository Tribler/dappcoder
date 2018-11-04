import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class ReviewItem(QWidget):

    def __init__(self, parent, review_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('gui', 'qt_resources', 'review_item.ui'), self)

        self.review_info = review_info
        if self.review_info['public_key'] == self.window().profile_info['public_key']:
            self.name_label.setText("Your review")
            self.name_label.setStyleSheet("font-weight: bold;")
        else:
            self.name_label.setText("Review by %s" % self.review_info['username'])
