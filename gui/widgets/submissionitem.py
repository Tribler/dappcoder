import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class SubmissionItem(QWidget):

    def __init__(self, parent, submission_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('gui', 'qt_resources', 'submission_item.ui'), self)

        self.submission_info = submission_info
        if self.submission_info['public_key'] == self.window().profile_info['public_key']:
            self.name_label.setText("Your submission")
            self.name_label.setStyleSheet("font-weight: bold;")
        else:
            self.name_label.setText("Submission by %s" % self.submission_info['username'])
        self.detail_label.setText("%d/%d reviews" % (self.submission_info['num_reviews'], self.submission_info['min_reviews']))
