import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class NotificationsListItem(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'notification_list_item.ui'), self)
