from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui import PROJECT_PAGE
from gui.requestmanager import RequestManager
from gui.widgets.jobitem import JobItem


class ProjectsPage(QWidget):

    def initialize(self):
        self.window().jobs_list.itemClicked.connect(self.on_job_clicked)

    def on_job_clicked(self):
        selected_items = self.window().jobs_list.selectedItems()
        if not selected_items:
            return
        selected_item = selected_items[0]
        item_widget = self.window().jobs_list.itemWidget(selected_item)

        self.window().project_page.load_project(item_widget.job_info['public_key'], item_widget.job_info['id'])
        self.window().project_back_container.show()
        self.window().stackedWidget.setCurrentIndex(PROJECT_PAGE)

    def on_projects(self, data):
        self.window().jobs_list.clear()
        for project in data['projects']:
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 50))
            widget_item = JobItem(self.window().jobs_list, project)
            self.window().jobs_list.addItem(item)
            self.window().jobs_list.setItemWidget(item, widget_item)

    def load_jobs(self):
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/projects", self.on_projects)
