import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class JobItem(QWidget):

    def __init__(self, parent, job_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'job_item.ui'), self)

        self.job_info = job_info
        self.job_name_label.setText(self.job_info['name'])
