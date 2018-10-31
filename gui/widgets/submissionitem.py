import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class SubmissionItem(QWidget):

    def __init__(self, parent, submission_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'submission_item.ui'), self)

        self.submission_info = submission_info
