import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from gui.util import pretty_date


class TimelineItem(QWidget):

    def __init__(self, parent, item_dict):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'timeline_item.ui'), self)

        self.item_dict = item_dict
        self.time_label.setText(pretty_date(self.item_dict['timestamp'] / 1000))
        user_part = "User %s" % self.item_dict['username'] if self.item_dict['public_key'] != self.window().profile_info['public_key'] else "You"
        if self.item_dict['type'] == 'created_job':
            self.main_text_label.setText("%s created a new job: %s" % (user_part, self.item_dict['job_name']))
        elif self.item_dict['type'] == 'created_submission':
            self.main_text_label.setText("%s made a submission for job: %s" % (user_part, self.item_dict['job_name']))
        elif self.item_dict['type'] == 'profile_import':
            self.main_text_label.setText("%s imported a %s profile" % (user_part, self.item_dict['platform']))
