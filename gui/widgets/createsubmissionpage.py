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
        self.window().add_submission_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(PROJECT_PAGE)

    def on_submission_created(self, data):
        if not data or 'success' not in data or not data['success']:
            ConfirmationDialog.show_error(self.window(), "Error", "Error when creating the submission!")
            return

        self.window().load_left_menu()
        self.window().stackedWidget.setCurrentIndex(PROJECT_PAGE)
        self.window().project_add_submission_button.setEnabled(False)
        self.window().project_page.reload_project()
        ConfirmationDialog.show_error(self.window(), "Success", "Your submission has been created!")

    def on_create_submission_clicked(self):
        request_manager = RequestManager()
        submission_text = self.window().submission_input.toPlainText().encode('hex')
        post_data = str("project_pk=%s&project_id=%s&submission=%s" % (self.active_project_pk, self.active_project_id, submission_text))
        request_manager.perform_request("dappcrowd/submissions", self.on_submission_created, data=post_data, method="PUT")
