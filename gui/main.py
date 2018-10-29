import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem

from gui.widgets.leftmenuitem import LeftMenuItem
from gui.widgets.timelineitem import TimelineItem
from widgets.leftmenuheaderitem import LeftMenuHeaderItem
from widgets.notificationspane import NotificationsPanel


class DAppCrowdWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi(os.path.join('qt_resources', 'mainwindow.ui'), self)

        self.notifications_panel = NotificationsPanel(self)
        self.notifications_panel.resize(300, 150)
        self.notifications_panel.move(self.width() - self.notifications_panel.width() - 15, self.top_bar.height())
        self.notifications_panel.hide()

        self.notifications_button.clicked.connect(self.on_notifications_button_clicked)
        self.top_menu_button.clicked.connect(self.on_top_bar_button_clicked)

        self.load_left_menu()
        self.load_timeline()

    def on_notifications_button_clicked(self):
        if self.notifications_panel.isVisible():
            self.notifications_panel.hide()
        else:
            self.notifications_panel.show()
            self.notifications_panel.load()

    def on_top_bar_button_clicked(self):
        if self.left_menu.isVisible():
            self.left_menu.hide()
        else:
            self.left_menu.show()

    def load_left_menu(self):
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list)
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

        for _ in range(0, 2):
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 32))
            widget_item = LeftMenuItem(self.left_menu_list)
            self.left_menu_list.addItem(item)
            self.left_menu_list.setItemWidget(item, widget_item)

        # Submissions
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list)
        widget_item.main_title_label.setText("My Submissions")
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

        for i in range(0, 2):
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 32))
            widget_item = LeftMenuItem(self.left_menu_list)
            widget_item.detail_label.setText("3/10 reviews")
            if i == 1:
                widget_item.status_button.setIcon(QIcon(QPixmap(os.path.join('images', 'checkmark.png'))))
                widget_item.detail_label.setText("Accepted")
            self.left_menu_list.addItem(item)
            self.left_menu_list.setItemWidget(item, widget_item)

        # Reviews
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list)
        widget_item.main_title_label.setText("My Reviews")
        widget_item.new_button.hide()
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

    def load_timeline(self):
        for _ in range(0, 2):
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 80))
            widget_item = TimelineItem(self.timeline_list)
            self.timeline_list.addItem(item)
            self.timeline_list.setItemWidget(item, widget_item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAppCrowdWindow()
    window.setWindowTitle("DAppCrowd")
    window.show()
    sys.exit(app.exec_())
