import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget


class SkillItem(QWidget):

    def __init__(self, parent, skill_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('qt_resources', 'skill_item.ui'), self)

        self.skill_info = skill_info
        self.name_label.setText(self.skill_info['name'])
        self.endorsements_label.setText("(%d endorsements)" % self.skill_info['endorsements'])
        if self.skill_info['did_endorse']:
            self.endorse_button.hide()
