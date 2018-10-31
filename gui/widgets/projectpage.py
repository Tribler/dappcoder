from PyQt5.QtWidgets import QWidget

from gui import ADD_SUBMISSION_PAGE
from gui.requestmanager import RequestManager


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

    def on_project_info(self, data):
        self.window().project_name_label.setText(data['project']['name'])
        self.window().project_deadline_label.setText(data['project']['deadline'])

    def load_project(self, project_pk, project_id):
        self.active_project_pk = project_pk
        self.active_project_id = project_id
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/projects/%s/%d" % (project_pk, project_id), self.on_project_info)
