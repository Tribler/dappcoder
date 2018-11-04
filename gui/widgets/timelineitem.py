import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from gui.util import pretty_date


class TimelineItem(QWidget):

    def __init__(self, parent, item_dict):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('gui', 'qt_resources', 'timeline_item.ui'), self)

        self.item_dict = item_dict
        self.time_label.setText(pretty_date(self.item_dict['timestamp'] / 1000))
        is_you = self.item_dict['public_key'] == self.window().profile_info['public_key']
        user_part = "You" if is_you else "User %s" % self.item_dict['username']
        if self.item_dict['type'] == 'created_job':
            self.main_text_label.setText("%s created a new job: %s." % (user_part, self.item_dict['job_name']))
        elif self.item_dict['type'] == 'created_submission':
            self.main_text_label.setText("%s made a submission for job: %s." % (user_part, self.item_dict['job_name']))
        elif self.item_dict['type'] == 'profile_import':
            self.main_text_label.setText("%s imported a %s profile." % (user_part, self.item_dict['platform']))
        elif self.item_dict['type'] == 'added_skill':
            self.main_text_label.setText("%s added a skill (%s) to %s profile." % (user_part, self.item_dict['skill_name'], 'your' if is_you else 'their'))
        elif self.item_dict['type'] == 'endorsement':
            self.main_text_label.setText("%s endorsed user %s for skill '%s'." % (user_part, self.item_dict['endorsed_username'], self.item_dict['skill_name']))
