import json

from twisted.web import http

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint
from pyipv8.ipv8.database import database_blob


class UsersEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.putChild("myprofile", MyProfileEndpoint(ipv8, ipfs_api))

    def getChild(self, path, request):
        return SpecificUserEndpoint(self.ipv8, self.ipfs_api, path)

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        return json.dumps({"users": trustchain.persistence.get_users_list()})


class MyProfileEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.putChild("skills", MyProfileSkillsEndpoint(ipv8, ipfs_api))

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        my_pub_key = trustchain.my_peer.public_key.key_to_bin()
        return json.dumps({"profile": trustchain.persistence.get_detailled_user_info(my_pub_key)})


class MyProfileSkillsEndpoint(DAppCrowdEndpoint):

    def render_PUT(self, request):
        parameters = http.parse_qs(request.content.read(), 1)
        if 'name' not in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "missing name parameter"})

        trustchain = self.get_trustchain()
        trustchain.add_skill(parameters['name'][0])

        return json.dumps({"success": True})


class SpecificUserEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, pub_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.putChild("timeline", SpecificUserTimelineEndpoint(ipv8, ipfs_api, pub_key))
        self.putChild("skills", SpecificUserSkillsEndpoint(ipv8, ipfs_api, pub_key))
        self.pub_key = pub_key

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        return json.dumps({"user": trustchain.persistence.get_detailled_user_info(self.pub_key.decode('hex'))})


class SpecificUserTimelineEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, pub_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.pub_key = pub_key

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        blocks_of_user = trustchain.persistence._getall(u"WHERE public_key = ?", (database_blob(self.pub_key.decode('hex')),))
        blocks_of_user = sorted(blocks_of_user, reverse=True, key=lambda block: block.timestamp)
        timeline_list = []

        for block in blocks_of_user:
            if block.type == 'dappcrowd_github':
                timeline_list.append({
                    "type": "github_import",
                    "username": block.transaction['username']
                })
            elif block.type == 'dappcrowd_apprequest':
                apprequest_info = block.transaction
                apprequest_info['type'] = 'dappcrowd_apprequest'
                timeline_list.append(apprequest_info)
            elif block.type == 'dappcrowd_submission':
                submission_info = block.transaction
                submission_info['type'] = 'dappcrowd_submission'
            elif block.type == 'dappcrowd_review':
                review_info = block.transaction
                review_info['type'] = 'dappcrowd_review'

        return json.dumps({"timeline": timeline_list})


class SpecificUserSkillsEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, pub_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.pub_key = pub_key

    def render_PUT(self, request):
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['public_key', 'block_num']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        trustchain = self.get_trustchain()
        trustchain.endorse_skill(parameters['public_key'][0].decode('hex'), parameters['block_num'][0])

        return json.dumps({"success": True})
