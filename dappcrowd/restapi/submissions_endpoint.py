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

    def render_PUT(self, request):
        """
        Create a new submission for an app request.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['apprequest_pk', 'apprequest_id', 'submission']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        # Step 1: upload the submission to IPFS
        specs_pointer = self.ipfs_api.add(parameters['submission'][0])['Hash']

        # Step 2: publish it on TrustChain
        trustchain = self.get_trustchain()
        tx = {
            'apprequest_pk': parameters['apprequest_pk'][0],
            'apprequest_id': parameters['apprequest_id'][0],
            'submission': specs_pointer
        }

        def on_block_created(blocks):
            dappcrowd_overlay = self.get_dappcrowd_overlay()
            dappcrowd_overlay.persistence.add_submission(blocks[0])
            request.write(json.dumps({"success": True}))
            request.finish()

        trustchain.create_source_block(block_type='dappcrowd_submission', transaction=tx).addCallback(on_block_created)

        return NOT_DONE_YET
