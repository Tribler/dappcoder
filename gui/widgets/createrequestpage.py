from PyQt5.QtWidgets import QWidget

from gui import PROJECT_PAGE
from gui.dialogs.confirmationdialog import ConfirmationDialog
from gui.requestmanager import RequestManager


class CreateRequestPage(QWidget):

    def initialize(self):
        self.window().create_app_request_button.clicked.connect(self.on_create_app_request_clicked)

    def on_app_request_created(self, data):
        if not data or 'success' not in data or not data['success']:
            ConfirmationDialog.show_error(self.window(), "Error", "Error when creating the application request!")
            return

        self.window().load_my_profile()

        self.window().project_page.load_project(self.window().profile_info['public_key'], data['id'])
        self.window().project_back_container.hide()
        self.window().stackedWidget.setCurrentIndex(PROJECT_PAGE)
        ConfirmationDialog.show_error(self.window(), "Success", "Your job has been created!")

    def on_create_app_request_clicked(self):
        name = self.window().create_app_request_name_input.text()
        specifications = self.window().create_app_request_specifications_input.toPlainText().encode('hex')
        deadline = "2018-12-01"
        reward = 300
        currency = "EUR"
        min_reviews = 3

        request_manager = RequestManager()
        post_data = str("name=%s&specifications=%s&deadline=%s&reward=%d&currency=%s&min_reviews=%d" % (name, specifications, deadline, reward, currency, min_reviews))
        request_manager.perform_request("dappcrowd/projects", self.on_app_request_created, data=post_data, method="PUT")
