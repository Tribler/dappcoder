from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui import PROFILE_PAGE
from gui.requestmanager import RequestManager
from gui.widgets.useritem import UserItem


class UsersPage(QWidget):

    def initialize(self):
        self.window().users_list.itemClicked.connect(self.on_item_clicked)

    def on_users(self, data):
        self.window().users_list.clear()
        for user_dict in data['users']:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 40))
            widget_item = UserItem(self.window().users_list, user_dict)
            self.window().users_list.addItem(item)
            self.window().users_list.setItemWidget(item, widget_item)

    def load_users(self):
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users", self.on_users)

    def on_item_clicked(self):
        selected_item = self.window().users_list.selectedItems()[0]
        item_widget = self.window().users_list.itemWidget(selected_item)
        self.window().users_list.clearSelection()

        self.window().profile_page.load_user(item_widget.user_dict['public_key'])
        self.window().profile_back_container.show()
        self.window().stackedWidget.setCurrentIndex(PROFILE_PAGE)
