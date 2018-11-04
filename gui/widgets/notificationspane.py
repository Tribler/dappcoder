import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui.widgets.notificationslistitem import NotificationsListItem


class NotificationsPanel(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent)

        uic.loadUi(os.path.join('gui', 'qt_resources', 'notifications.ui'), self)

    def load(self):
        # TODO use REST API
        self.notifications_list.clear()
        item = QListWidgetItem()
        widget_item = NotificationsListItem(self.notifications_list)
        self.notifications_list.addItem(item)
        self.notifications_list.setItemWidget(item, widget_item)
