import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class TimelineItem(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'timeline_item.ui'), self)