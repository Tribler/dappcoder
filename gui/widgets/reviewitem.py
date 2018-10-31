import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class ReviewItem(QWidget):

    def __init__(self, parent, review_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'review_item.ui'), self)

        self.review_info = review_info
