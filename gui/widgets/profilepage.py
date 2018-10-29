from PyQt5.QtWidgets import QWidget

from gui.requestmanager import RequestManager


class ProfilePage(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.active_user = None

    def on_user_info(self, data):
        print data
        is_me = self.active_user == self.window().profile_info['public_key']
        if is_me:
            self.window().profile_header_label.setText("Your DevID")
        else:
            self.window().profile_header_label.setText("DevID of user '%s'" % data['user']['username'])

        if data['user']['verified']:
            self.window().profile_verified_label.show()

        if not data['user']['github_info']:
            if is_me:
                self.window().connect_github_container.show()
                self.window().no_github_imported_label.hide()
            else:
                self.window().connect_github_container.hide()
                self.window().no_github_imported_label.show()

        if not data['user']['bitbucket_info']:
            if is_me:
                self.window().connect_bitbucket_container.show()
                self.window().no_bitbucket_imported_label.hide()
            else:
                self.window().connect_bitbucket_container.hide()
                self.window().no_bitbucket_imported_label.show()

    def load_user(self, public_key):
        self.active_user = public_key
        self.window().profile_verified_label.hide()

        request_manager = RequestManager()
        request_manager.perform_request("dappcrowd/users/%s" % public_key.encode('hex'), self.on_user_info)
