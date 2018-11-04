import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

from gui import BUTTON_TYPE_CONFIRM, BUTTON_TYPE_NORMAL
from gui.dialogs.confirmationdialog import ConfirmationDialog
from gui.requestmanager import RequestManager


class SkillItem(QWidget):

    def __init__(self, parent, profile_page, skill_info):
        QWidget.__init__(self, parent)
        uic.loadUi(os.path.join('gui', 'qt_resources', 'skill_item.ui'), self)
        self.profile_page = profile_page
        self.dialog = None

        self.skill_info = skill_info
        self.name_label.setText(self.skill_info['name'])
        self.endorsements_label.setText("(%d endorsements)" % self.skill_info['endorsements'])
        if self.skill_info['did_endorse']:
            self.endorse_button.hide()

        self.endorse_button.clicked.connect(self.on_endorse_button_clicked)

    def on_endorse_button_clicked(self):
        if not self.dialog:
            self.dialog = ConfirmationDialog(self.window(), "Give endorsement",
                                             "Are you sure that you want to endorse the skill '%s'?" % self.skill_info['name'],
                                             [('ENDORSE', BUTTON_TYPE_CONFIRM), ('CANCEL', BUTTON_TYPE_NORMAL)])
            self.dialog.button_clicked.connect(self.on_endorse_button_dialog_clicked)
            self.dialog.show()

    def on_endorse_button_dialog_clicked(self, action):
        if action == 0:
            # Endorse the skill
            request_manager = RequestManager()
            post_data = str("block_num=%d" % self.skill_info['block_num'])
            request_manager.perform_request("dappcrowd/users/%s/skills" % self.profile_page.active_user, self.on_skill_endorsed, data=post_data, method="PUT")
        self.dialog.close()
        self.dialog = None

    def on_skill_endorsed(self, _):
        self.profile_page.load_user(self.profile_page.active_user)
