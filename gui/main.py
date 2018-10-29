import logging
import os
import sys

import ipfsapi
from PyQt5 import uic
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem

from gui import TIMELINE_PAGE, LEFT_MENU_APPREQUEST_TYPE, LEFT_MENU_SUBMISSION_TYPE, LEFT_MENU_REVIEW_TYPE, USERS_PAGE
from gui.dialogs.confirmationdialog import ConfirmationDialog
from gui.requestmanager import RequestManager
from gui.widgets.leftmenuitem import LeftMenuItem
from gui.widgets.timelineitem import TimelineItem
from widgets.leftmenuheaderitem import LeftMenuHeaderItem
from widgets.notificationspane import NotificationsPanel


class DAppCrowdWindow(QMainWindow):
    resize_event = pyqtSignal()

    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi(os.path.join('qt_resources', 'mainwindow.ui'), self)
        RequestManager.window = self

        self.profile_info = None
        self.my_app_requests = []
        self.my_submissions = []

        # Initialize logging
        root = logging.getLogger()
        root.setLevel(logging.WARNING)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize IPFS API
        self.ipfs_api = ipfsapi.connect('127.0.0.1', 5001)

        # Initialize pages
        self.make_app_request_page.initialize()
        self.users_page.initialize()

        self.notifications_panel = NotificationsPanel(self)
        self.notifications_panel.resize(300, 150)
        self.notifications_panel.move(self.width() - self.notifications_panel.width() - 15, self.top_bar.height())
        self.notifications_panel.hide()

        self.notifications_button.clicked.connect(self.on_notifications_button_clicked)
        self.top_menu_button.clicked.connect(self.on_top_bar_button_clicked)
        self.top_menu_users_button.clicked.connect(self.on_top_bar_users_button_clicked)

        self.stackedWidget.setCurrentIndex(TIMELINE_PAGE)

        # Load your profile information first
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/myprofile", self.on_my_profile)

        self.left_menu.hide()
        self.top_menu_button.hide()

    def on_my_profile(self, data):
        if not data:
            ConfirmationDialog.show_error(self, "Profile loading failed", "Your own profile data could not be loaded!")
            return

        self.profile_info = data["profile"]
        self.left_menu.show()
        self.top_menu_button.show()

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

    def on_top_bar_users_button_clicked(self):
        self.stackedWidget.setCurrentIndex(USERS_PAGE)
        self.users_page.load_users()

    def on_my_apprequests(self, data):
        self.my_app_requests = []
        for apprequest in data['apprequests']:
            if apprequest['public_key'] == self.profile_info['public_key']:
                self.my_app_requests.append(apprequest)

        self.redraw_left_menu()

        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/submissions", self.on_my_submissions)

    def on_my_submissions(self, data):
        for submission in data['submissions']:
            if submission['public_key'] == self.profile_info['public_key']:
                self.my_submissions.append(submission)

        self.redraw_left_menu()

        # TODO fetch reviews

    def redraw_left_menu(self):
        self.left_menu_list.clear()

        # My app requests header
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list, LEFT_MENU_APPREQUEST_TYPE)
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

        for apprequest in self.my_app_requests:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 32))
            widget_item = LeftMenuItem(self.left_menu_list, LEFT_MENU_APPREQUEST_TYPE, apprequest)
            self.left_menu_list.addItem(item)
            self.left_menu_list.setItemWidget(item, widget_item)

        # Submissions header
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list, LEFT_MENU_SUBMISSION_TYPE)
        widget_item.main_title_label.setText("My Submissions")
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

        for submission in self.my_submissions:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 32))
            widget_item = LeftMenuItem(self.left_menu_list, LEFT_MENU_SUBMISSION_TYPE, submission)
            widget_item.detail_label.setText("3/10 reviews")
            self.left_menu_list.addItem(item)
            self.left_menu_list.setItemWidget(item, widget_item)

        # Reviews
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list, LEFT_MENU_REVIEW_TYPE)
        widget_item.main_title_label.setText("My Reviews")
        widget_item.new_button.hide()
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

    def load_left_menu(self):
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/apprequests", self.on_my_apprequests)

    def load_timeline(self):
        for _ in range(0, 2):
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 80))
            widget_item = TimelineItem(self.timeline_list)
            self.timeline_list.addItem(item)
            self.timeline_list.setItemWidget(item, widget_item)

    def resizeEvent(self, _):
        self.resize_event.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAppCrowdWindow()
    window.setWindowTitle("DAppCrowd")
    window.show()
    sys.exit(app.exec_())
