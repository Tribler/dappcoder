from PyQt5.QtWidgets import QWidget

from gui import SUBMISSION_PAGE
from gui.dialogs.confirmationdialog import ConfirmationDialog
from gui.requestmanager import RequestManager


class CreateReviewPage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_submission_pk = None
        self.active_submission_id = None

    def initialize(self):
        self.window().make_review_button.clicked.connect(self.on_create_review_clicked)
        self.window().add_review_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(SUBMISSION_PAGE)

    def on_review_created(self, data):
        if not data or 'success' not in data or not data['success']:
            ConfirmationDialog.show_error(self.window(), "Error", "Error when creating the review!")
            return

        self.window().load_left_menu()
        self.window().stackedWidget.setCurrentIndex(SUBMISSION_PAGE)
        ConfirmationDialog.show_error(self.window(), "Success", "Your review has been created!")

    def on_create_review_clicked(self):
        request_manager = RequestManager()
        post_data = str("submission_pk=%s&submission_id=%s&review=test" % (self.active_submission_pk, self.active_submission_id))
        request_manager.perform_request("dappcrowd/reviews", self.on_review_created, data=post_data, method="PUT")
