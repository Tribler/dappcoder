from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui import ADD_REVIEW_PAGE, REVIEW_PAGE, PROJECT_PAGE
from gui.requestmanager import RequestManager
from gui.widgets.reviewitem import ReviewItem


class SubmissionPage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_submission_pk = None
        self.active_submission_id = None

    def on_add_review_clicked(self):
        self.window().make_review_page.active_submission_pk = self.active_submission_pk
        self.window().make_review_page.active_submission_id = self.active_submission_id
        self.window().stackedWidget.setCurrentIndex(ADD_REVIEW_PAGE)

    def initialize(self):
        self.window().submission_add_review_button.clicked.connect(self.on_add_review_clicked)
        self.window().submission_reviews_list.itemClicked.connect(self.on_review_clicked)
        self.window().submission_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(PROJECT_PAGE)

    def on_review_clicked(self):
        selected_item = self.window().submission_reviews_list.selectedItems()[0]
        item_widget = self.window().submission_reviews_list.itemWidget(selected_item)
        self.window().submission_reviews_list.clearSelection()

        self.window().review_page.load_review(item_widget.review_info['public_key'], item_widget.review_info['id'])
        self.window().review_back_container.show()
        self.window().stackedWidget.setCurrentIndex(REVIEW_PAGE)

    def on_reviews(self, data):
        self.window().submission_reviews_list.clear()
        for review in data['reviews']:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 40))
            widget_item = ReviewItem(self.window().submission_reviews_list, review)
            self.window().submission_reviews_list.addItem(item)
            self.window().submission_reviews_list.setItemWidget(item, widget_item)

    def on_submission_info(self, data):
        if data['submission']['public_key'] == self.window().profile_info['public_key'] or data['submission']['did_review']:
            self.window().submission_add_review_button.setEnabled(False)
        else:
            self.window().submission_add_review_button.setEnabled(True)

        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/submissions/%s/%d/reviews" % (self.active_submission_pk, self.active_submission_id), self.on_reviews)

    def load_submission(self, submission_pk, submission_id):
        self.active_submission_pk = submission_pk
        self.active_submission_id = submission_id
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/submissions/%s/%d" % (submission_pk, submission_id), self.on_submission_info)
