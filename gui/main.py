import logging
import os
import sys

import ipfsapi
from PyQt5 import uic
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QListWidgetItem

from gui import TIMELINE_PAGE, LEFT_MENU_APPREQUEST_TYPE, LEFT_MENU_SUBMISSION_TYPE, LEFT_MENU_REVIEW_TYPE, USERS_PAGE, \
    PROFILE_PAGE, PROJECT_PAGE, PROJECTS_PAGE, SUBMISSION_PAGE, REVIEW_PAGE
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
        self.my_projects = []
        self.my_submissions = []
        self.my_reviews = []

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
        self.profile_page.initialize()
        self.project_page.initialize()
        self.make_submission_page.initialize()
        self.projects_page.initialize()
        self.submission_page.initialize()
        self.make_review_page.initialize()
        self.review_page.initialize()

        self.notifications_panel = NotificationsPanel(self)
        self.notifications_panel.resize(300, 150)
        self.notifications_panel.move(self.width() - self.notifications_panel.width() - 15, self.top_bar.height())
        self.notifications_panel.hide()

        self.notifications_button.clicked.connect(self.on_notifications_button_clicked)
        self.top_menu_button.clicked.connect(self.on_top_bar_button_clicked)
        self.top_menu_jobs_button.clicked.connect(self.on_top_bar_jobs_button_clicked)
        self.top_menu_users_button.clicked.connect(self.on_top_bar_users_button_clicked)
        self.user_profile_button.clicked.connect(self.on_user_profile_button_clicked)
        self.left_menu_list.itemClicked.connect(self.on_left_menu_item_clicked)
        self.app_name_button.clicked.connect(self.on_app_name_button_clicked)

        self.stackedWidget.setCurrentIndex(TIMELINE_PAGE)

        # Load your profile information first
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/myprofile", self.on_my_profile)

        self.left_menu.hide()
        self.top_menu_button.hide()
        self.stackedWidget.hide()

    def on_app_name_button_clicked(self):
        self.load_timeline()
        self.stackedWidget.setCurrentIndex(TIMELINE_PAGE)

    def on_left_menu_item_clicked(self):
        selected_items = self.left_menu_list.selectedItems()
        if not selected_items:
            return
        selected_item = selected_items[0]
        item_widget = self.left_menu_list.itemWidget(selected_item)
        self.left_menu_list.clearSelection()
        if isinstance(item_widget, LeftMenuHeaderItem):
            pass
        elif item_widget.type == LEFT_MENU_APPREQUEST_TYPE:
            self.project_page.load_project(item_widget.data_dict['public_key'], item_widget.data_dict['id'])
            self.window().project_back_container.hide()
            self.stackedWidget.setCurrentIndex(PROJECT_PAGE)
        elif item_widget.type == LEFT_MENU_SUBMISSION_TYPE:
            self.submission_page.load_submission(item_widget.data_dict['public_key'], item_widget.data_dict['id'])
            self.window().submission_back_container.hide()
            self.stackedWidget.setCurrentIndex(SUBMISSION_PAGE)
        elif item_widget.type == LEFT_MENU_REVIEW_TYPE:
            self.review_page.load_review(item_widget.data_dict['public_key'], item_widget.data_dict['id'])
            self.window().review_back_container.hide()
            self.stackedWidget.setCurrentIndex(REVIEW_PAGE)

    def on_my_profile(self, data):
        if not data:
            ConfirmationDialog.show_error(self, "Profile loading failed", "Your own profile data could not be loaded!")
            return

        self.profile_info = data["profile"]
        self.left_menu.show()
        self.top_menu_button.show()
        self.stackedWidget.show()

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

    def on_user_profile_button_clicked(self):
        self.window().profile_back_container.hide()
        self.stackedWidget.setCurrentIndex(PROFILE_PAGE)
        if self.profile_page.active_user != self.profile_info['public_key']:
            self.profile_page.load_user(self.profile_info['public_key'])

    def on_top_bar_jobs_button_clicked(self):
        self.stackedWidget.setCurrentIndex(PROJECTS_PAGE)
        self.projects_page.load_jobs()

    def on_my_projects(self, data):
        self.my_projects = []
        for project in data['projects']:
            if project['public_key'] == self.profile_info['public_key']:
                self.my_projects.append(project)

        self.redraw_left_menu()

        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/myprofile/submissions", self.on_my_submissions)

    def on_my_submissions(self, data):
        self.my_submissions = data['submissions']
        self.redraw_left_menu()

        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/myprofile/reviews", self.on_my_reviews)

    def on_my_reviews(self, data):
        self.my_reviews = data['reviews']
        self.redraw_left_menu()

    def redraw_left_menu(self):
        self.left_menu_list.clear()

        # My Projects header
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list, LEFT_MENU_APPREQUEST_TYPE)
        widget_item.main_title_label.setText("My Jobs")
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

        for apprequest in self.my_projects:
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
            self.left_menu_list.addItem(item)
            self.left_menu_list.setItemWidget(item, widget_item)

        # Reviews
        header_item = QListWidgetItem()
        header_item.setSizeHint(QSize(-1, 40))
        widget_item = LeftMenuHeaderItem(self.left_menu_list, LEFT_MENU_REVIEW_TYPE)
        widget_item.main_title_label.setText("My Reviews")
        self.left_menu_list.addItem(header_item)
        self.left_menu_list.setItemWidget(header_item, widget_item)

        for review in self.my_reviews:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 32))
            widget_item = LeftMenuItem(self.left_menu_list, LEFT_MENU_REVIEW_TYPE, review)
            self.left_menu_list.addItem(item)
            self.left_menu_list.setItemWidget(item, widget_item)

    def load_left_menu(self):
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/projects", self.on_my_projects)

    def on_timeline_info(self, data):
        self.timeline_list.clear()
        for timeline_item in data['timeline']:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 80))
            widget_item = TimelineItem(self.timeline_list, timeline_item)
            self.timeline_list.addItem(item)
            self.timeline_list.setItemWidget(item, widget_item)

    def load_timeline(self):
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/timeline", self.on_timeline_info)

    def resizeEvent(self, _):
        self.resize_event.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAppCrowdWindow()
    window.setWindowTitle("DAppCrowd")
    window.show()
    sys.exit(app.exec_())
