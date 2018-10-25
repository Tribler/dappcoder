import json

from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class ReviewsEndpoint(DAppCrowdEndpoint):

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

        # Step 1: upload the review to IPFS
        specs_pointer = self.ipfs_api.add(parameters['review'][0])['Hash']

        # Step 2: publish it on TrustChain
        trustchain = self.get_trustchain()
        tx = {
            'submission_pk': parameters['submission_pk'][0],
            'submission_id': parameters['submission_id'][0],
            'review': specs_pointer
        }

        def on_block_created(blocks):
            dappcrowd_overlay = self.get_dappcrowd_overlay()
            dappcrowd_overlay.persistence.add_review(blocks[0])
            request.write(json.dumps({"success": True}))
            request.finish()

        trustchain.create_source_block(block_type='dappcrowd_review', transaction=tx).addCallback(
            on_block_created)

        return NOT_DONE_YET