from PyQt5.QtWidgets import QWidget

from gui import SUBMISSION_PAGE
from gui.requestmanager import RequestManager


class ReviewPage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_review_pk = None
        self.active_review_id = None

    def initialize(self):
        self.window().review_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(SUBMISSION_PAGE)

    def on_review_info(self, data):
        self.window().review_text_input.setPlainText(data['review']['review'].decode('hex'))

    def load_review(self, review_pk, review_id):
        self.active_review_pk = review_pk
        self.active_review_id = review_id
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/reviews/%s/%d" % (review_pk, review_id), self.on_review_info)
