from PyQt5.QtWidgets import QWidget

from gui import SUBMISSION_PAGE
from gui.requestmanager import RequestManager
from gui.util import pretty_date


class ReviewPage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_review_pk = None
        self.active_review_id = None
        self.review_info = None

    def initialize(self):
        self.window().review_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(SUBMISSION_PAGE)

    def on_review_info(self, data):
        self.review_info = data
        user_made = "you" if self.review_info['review']['public_key'] == self.window().profile_info['public_key'] else self.review_info['review']['username']
        self.window().review_details_label.setText("This review was made by %s (%s)" % (user_made, pretty_date(self.review_info['review']['timestamp'] / 1000)))
        self.window().review_text_input.setPlainText(data['review']['review'].decode('hex'))

    def load_review(self, review_pk, review_id):
        self.active_review_pk = review_pk
        self.active_review_id = review_id
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/reviews/%s/%d" % (review_pk, review_id), self.on_review_info)
