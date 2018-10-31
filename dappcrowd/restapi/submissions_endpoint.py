import json

from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class SubmissionsEndpoint(DAppCrowdEndpoint):

    def render_GET(self, request):
        """
        Get all submissions.
        """
        dappcrowd_overlay = self.get_dappcrowd_overlay()
        return json.dumps({"submissions": dappcrowd_overlay.persistence.get_submissions()})

    def getChild(self, path, request):
        return SubmissionPKEndpoint(self.ipv8, self.ipfs_api, path)

    def render_PUT(self, request):
        """
        Create a new submission for an app request.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['project_pk', 'project_id', 'submission']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        def on_block_created(blocks):
            request.write(json.dumps({"success": True}))
            request.finish()

        self.get_dappcrowd_overlay().create_submission(parameters['project_pk'][0].decode('hex'), parameters['project_id'][0], parameters['submission'][0]).addCallback(on_block_created)

        return NOT_DONE_YET


class SubmissionPKEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key.decode('hex')

    def getChild(self, path, request):
        return SpecificSubmissionEndpoint(self.ipv8, self.ipfs_api, self.public_key, path)


class SpecificSubmissionEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key, submission_id):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key
        self.submission_id = submission_id
        self.putChild("reviews", SpecificSubmissionReviewsEndpoint(ipv8, ipfs_api, public_key, submission_id))

    def render_GET(self, request):
        if not self.get_dappcrowd_overlay().persistence.has_submission(self.public_key, self.submission_id):
            request.setResponseCode(http.NOT_FOUND)
            return json.dumps({"error": "the submission is not found"})

        return json.dumps({
            "submission": self.get_dappcrowd_overlay().persistence.get_submission(self.public_key, self.submission_id)
        })


class SpecificSubmissionReviewsEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key, submission_id):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key
        self.submission_id = submission_id

    def render_GET(self, request):
        if not self.get_dappcrowd_overlay().persistence.has_submission(self.public_key, self.submission_id):
            request.setResponseCode(http.NOT_FOUND)
            return json.dumps({"error": "the submission is not found"})

        return json.dumps({
            "reviews": self.get_dappcrowd_overlay().persistence.get_reviews(self.public_key, self.submission_id)
        })
