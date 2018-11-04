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
        self.putChild("submissions", MySubmissionsEndpoint(ipv8, ipfs_api))
        self.putChild("reviews", MyReviewsEndpoint(ipv8, ipfs_api))

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        my_pub_key = trustchain.my_peer.public_key.key_to_bin()
        profile_dict = trustchain.persistence.get_detailled_user_info(my_pub_key)
        profile_dict['total_jobs'] = len(self.get_dappcrowd_overlay().persistence.get_projects())
        return json.dumps({"profile": profile_dict})


class MyProfileSkillsEndpoint(DAppCrowdEndpoint):

    def render_PUT(self, request):
        parameters = http.parse_qs(request.content.read(), 1)
        if 'name' not in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "missing name parameter"})

        trustchain = self.get_trustchain()
        trustchain.add_skill(parameters['name'][0])

        return json.dumps({"success": True})


class MySubmissionsEndpoint(DAppCrowdEndpoint):

    def render_GET(self, request):
        my_public_key = self.get_trustchain().my_peer.public_key.key_to_bin()
        my_submissions = self.get_dappcrowd_overlay().persistence.get_submissions_for_user(my_public_key)
        return json.dumps({"submissions": my_submissions})


class MyReviewsEndpoint(DAppCrowdEndpoint):

    def render_GET(self, request):
        my_public_key = self.get_trustchain().my_peer.public_key.key_to_bin()
        my_reviews = self.get_dappcrowd_overlay().persistence.get_reviews_for_user(my_public_key)
        return json.dumps({"reviews": my_reviews})


class SpecificUserEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, pub_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.putChild("skills", SpecificUserSkillsEndpoint(ipv8, ipfs_api, pub_key))
        self.putChild("statistics", SpecificUserStatisticsEndpoint(ipv8, ipfs_api, pub_key))
        self.pub_key = pub_key

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        return json.dumps({"user": trustchain.persistence.get_detailled_user_info(self.pub_key.decode('hex'))})


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


class SpecificUserStatisticsEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, pub_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.pub_key = pub_key

    def render_GET(self, request):
        num_jobs = len(self.get_dappcrowd_overlay().persistence.get_projects_for_user(self.pub_key))
        num_submissions = len(self.get_dappcrowd_overlay().persistence.get_submissions_for_user(self.pub_key))
        num_reviews = len(self.get_dappcrowd_overlay().persistence.get_reviews_for_user(self.pub_key))

        return json.dumps({
            "statistics": {
                "num_jobs": num_jobs,
                "num_submissions": num_submissions,
                "num_reviews": num_reviews
            }
        })
