import json

from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class ReviewsEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.putChild("request", RequestReviewEndpoint(ipv8, ipfs_api))

    def getChild(self, path, request):
        return ReviewPKEndpoint(self.ipv8, self.ipfs_api, path)

    def render_GET(self, request):
        """
        Get all reviews for a specific submission.
        """
        if 'id' not in request.args or 'pk' not in request.args:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps("missing id or public key")

        dappcrowd_overlay = self.get_dappcrowd_overlay()
        return json.dumps({"reviews": dappcrowd_overlay.persistence.get_reviews(request.args['id'][0], request.args['pk'][0])})

    def render_PUT(self, request):
        """
        Create a new review for a submission.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['submission_id', 'submission_pk', 'review']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        def on_block_created(blocks):
            request.write(json.dumps({"success": True}))
            request.finish()

        self.get_dappcrowd_overlay().create_review(parameters['submission_pk'][0].decode('hex'), parameters['submission_id'][0], parameters['review'][0]).addCallback(on_block_created)

        return NOT_DONE_YET


class RequestReviewEndpoint(DAppCrowdEndpoint):

    def render_POST(self, request):
        """
        Request a specific user for a review.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['submission_id', 'requester_pk']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        self.get_dappcrowd_overlay().request_review(parameters['submission_id'][0], parameters['requester_pk'][0])

        return json.dumps({"success": True})


class ReviewPKEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key.decode('hex')

    def getChild(self, path, request):
        return SpecificReviewEndpoint(self.ipv8, self.ipfs_api, self.public_key, path)


class SpecificReviewEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key, review_id):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key
        self.review_id = review_id

    def render_GET(self, request):
        if not self.get_dappcrowd_overlay().persistence.has_review(self.public_key, self.review_id):
            request.setResponseCode(http.NOT_FOUND)
            return json.dumps({"error": "the review is not found"})

        return json.dumps({
            "review": self.get_dappcrowd_overlay().persistence.get_review(self.public_key, self.review_id)
        })
