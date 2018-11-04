from PyQt5.QtWidgets import QWidget

from gui import BUTTON_TYPE_NORMAL, BUTTON_TYPE_CONFIRM, USERS_PAGE
from gui.dialogs.confirmationdialog import ConfirmationDialog
from gui.requestmanager import RequestManager
from gui.widgets.skillitem import SkillItem


class ProfilePage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_user = None
        self.dialog = None
        self.user_data = None

    def initialize(self):
        self.window().add_skill_button.clicked.connect(self.on_add_skill_button_clicked)
        self.window().connect_github_button.clicked.connect(self.on_github_connect_clicked)
        self.window().profile_back_button.clicked.connect(self.on_back_button_clicked)

    def on_back_button_clicked(self):
        self.window().stackedWidget.setCurrentIndex(USERS_PAGE)

    def on_github_connect_clicked(self):
        self.dialog = ConfirmationDialog(self.window(), "Connect GitHub with your DevID",
                                         "You are about to connect your GitHub profile to DevID. To ensure that the account is really owned by you, you should add your member ID to your GitHub bio. This ID is: %s. When done, please enter your GitHub username in the field below:" % self.user_data['user']['mid'],
                                         [('ADD', BUTTON_TYPE_CONFIRM), ('CLOSE', BUTTON_TYPE_NORMAL)], show_input=True)
        self.dialog.dialog_widget.dialog_input.setPlaceholderText("GitHub username")
        self.dialog.button_clicked.connect(self.on_connect_github_dialog_button_clicked)
        self.dialog.show()

    def on_connect_github_dialog_button_clicked(self, action):
        if action == 0:
            # Add the skill
            request_manager = RequestManager()
            post_data = str("username=%s" % self.dialog.dialog_widget.dialog_input.text())
            request_manager.perform_request("dappcrowd/github/import", self.on_github_import_data, data=post_data,
                                            method="PUT")
        self.dialog.close()

    def on_github_import_data(self, data):
        # Reload the profile
        self.load_user(self.active_user)

    def on_add_skill_button_clicked(self):
        self.dialog = ConfirmationDialog(self.window(), "Add skill to your DevID", "Please enter the name of the skill you want to add to your DevID.", [('ADD', BUTTON_TYPE_CONFIRM), ('CLOSE', BUTTON_TYPE_NORMAL)], show_input=True)
        self.dialog.button_clicked.connect(self.on_add_skill_dialog_button_clicked)
        self.dialog.show()

    def on_add_skill_dialog_button_clicked(self, action):
        if action == 0:
            # Add the skill
            request_manager = RequestManager()
            post_data = str("name=%s" % self.dialog.dialog_widget.dialog_input.text())
            request_manager.perform_request("dappcrowd/users/myprofile/skills", self.on_skill_added, data=post_data, method="PUT")
        self.dialog.close()

    def on_skill_added(self, data):
        # Reload the profile
        self.load_user(self.active_user)

    def on_user_info(self, data):
        self.user_data = data
        is_me = self.active_user == self.window().profile_info['public_key']
        if is_me:
            self.window().profile_header_label.setText("Your DevID")
            self.window().add_skill_button.show()
        else:
            self.window().profile_header_label.setText("DevID of user '%s'" % data['user']['username'])
            self.window().add_skill_button.hide()

        if data['user']['verified']:
            self.window().profile_verified_label.show()

        if not data['user']['github_info']:
            if is_me:
                self.window().connect_github_container.show()
                self.window().no_github_imported_label.hide()
            else:
                self.window().connect_github_container.hide()
                self.window().no_github_imported_label.show()
            self.window().github_info_container.hide()
        else:
            self.window().connect_github_container.hide()
            self.window().no_github_imported_label.hide()
            self.window().github_info_container.show()
            self.window().github_username_label.setText(data['user']['github_info']['username'])
            self.window().github_followers_label.setText("%d" % data['user']['github_info']['followers'])

        if not data['user']['bitbucket_info']:
            if is_me:
                self.window().connect_bitbucket_container.show()
                self.window().no_bitbucket_imported_label.hide()
            else:
                self.window().connect_bitbucket_container.hide()
                self.window().no_bitbucket_imported_label.show()

        # Load the skills
        for i in reversed(range(self.window().skills_container.layout().count())):
            widget = self.window().skills_container.layout().itemAt(i).widget()
            if widget and widget != self.window().no_skills_added_label:
                self.window().skills_container.layout().itemAt(i).widget().setParent(None)

        for skill_info in data['user']['skills']:
            skill_widget = SkillItem(self.window().skills_container, self, skill_info)
            self.window().skills_container.layout().insertWidget(self.window().skills_container.layout().count() - 1, skill_widget)

        if len(data['user']['skills']) > 0:
            self.window().no_skills_added_label.hide()
        else:
            self.window().no_skills_added_label.show()
            if is_me:
                self.window().no_skills_added_label.setText("You have not added any skills to your profile.")
            else:
                self.window().no_skills_added_label.setText("This user did not add any skills to their profile.")

        # Load statistics
        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/%s/statistics" % self.active_user, self.on_statistics)

    def on_statistics(self, data):
        self.window().num_jobs_label.setText("%d" % data['statistics']['num_jobs'])
        self.window().num_submissions_label.setText("%d" % data['statistics']['num_submissions'])
        self.window().num_reviews_label.setText("%d" % data['statistics']['num_reviews'])

    def load_user(self, public_key):
        self.active_user = public_key
        self.window().profile_verified_label.hide()

        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/%s" % public_key, self.on_user_info)
