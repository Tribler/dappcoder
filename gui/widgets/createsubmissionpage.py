from PyQt5.QtWidgets import QWidget

from gui import PROJECT_PAGE
from gui.dialogs.confirmationdialog import ConfirmationDialog
from gui.requestmanager import RequestManager


class CreateSubmissionPage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_project_pk = None
        self.active_project_id = None

    def initialize(self):
        self.window().make_submission_button.clicked.connect(self.on_create_submission_clicked)

    def on_submission_created(self, data):
        if not data or 'success' not in data or not data['success']:
            ConfirmationDialog.show_error(self.window(), "Error", "Error when creating the submission!")
            return

        self.window().load_left_menu()
        self.window().stackedWidget.setCurrentIndex(PROJECT_PAGE)
        ConfirmationDialog.show_error(self.window(), "Success", "Your submission has been created!")

    def on_create_submission_clicked(self):
        request_manager = RequestManager()
        post_data = str("project_pk=%s&project_id=%s&submission=test" % (self.active_project_pk, self.active_project_id))
        request_manager.perform_request("dappcrowd/submissions", self.on_submission_created, data=post_data, method="PUT")
