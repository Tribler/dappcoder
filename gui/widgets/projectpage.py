from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui import ADD_SUBMISSION_PAGE, SUBMISSION_PAGE, PROJECTS_PAGE
from gui.requestmanager import RequestManager
from gui.widgets.submissionitem import SubmissionItem


class ProjectPage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_project_pk = None
        self.active_project_id = None

    def on_add_submission_clicked(self):
        self.window().make_submission_page.active_project_pk = self.active_project_pk
        self.window().make_submission_page.active_project_id = self.active_project_id
        self.window().stackedWidget.setCurrentIndex(ADD_SUBMISSION_PAGE)

    def initialize(self):
        self.window().project_add_submission_button.clicked.connect(self.on_add_submission_clicked)
        self.window().project_tab_widget.setCurrentIndex(0)

        self.window().project_submissions_list.itemClicked.connect(self.on_submission_clicked)
        self.window().project_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(PROJECTS_PAGE)

    def on_submission_clicked(self):
        selected_item = self.window().project_submissions_list.selectedItems()[0]
        item_widget = self.window().project_submissions_list.itemWidget(selected_item)
        self.window().project_submissions_list.clearSelection()

        self.window().submission_page.load_submission(item_widget.submission_info['public_key'], item_widget.submission_info['id'])
        self.window().submission_back_container.show()
        self.window().stackedWidget.setCurrentIndex(SUBMISSION_PAGE)

    def on_submissions(self, data):
        self.window().project_submissions_list.clear()
        for submission in data['submissions']:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 40))
            widget_item = SubmissionItem(self.window().project_submissions_list, submission)
            self.window().project_submissions_list.addItem(item)
            self.window().project_submissions_list.setItemWidget(item, widget_item)

    def on_project_info(self, data):
        self.window().project_name_label.setText(data['project']['name'])
        self.window().project_deadline_label.setText(data['project']['deadline'])

        if data['project']['public_key'] == self.window().profile_info['public_key'] or data['project']['made_submission']:
            self.window().project_add_submission_button.setEnabled(False)
        else:
            self.window().project_add_submission_button.setEnabled(True)

        # Load submissions
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/projects/%s/%d/submissions" % (self.active_project_pk, self.active_project_id), self.on_submissions)

    def load_project(self, project_pk, project_id):
        self.active_project_pk = project_pk
        self.active_project_id = project_id
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/projects/%s/%d" % (project_pk, project_id), self.on_project_info)
