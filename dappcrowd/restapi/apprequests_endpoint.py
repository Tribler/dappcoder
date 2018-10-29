import json

from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class AppRequestsEndpoint(DAppCrowdEndpoint):

    def render_GET(self, request):
        """
        Get all outstanding app requests.
        """
        dappcrowd_overlay = self.get_dappcrowd_overlay()
        return json.dumps({"apprequests": dappcrowd_overlay.persistence.get_app_requests()})

    def render_PUT(self, request):
        """
        Initiate a new app request.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['name', 'specifications', 'deadline', 'reward', 'currency', 'min_reviews']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        # TODO: notary signature! Contact third-party provider...
        # TODO add tests

        # Step 2: publish it on TrustChain
        trustchain = self.get_trustchain()
        tx = {
            'name': parameters['name'][0],
            'specifications': parameters['specifications'][0],
            'deadline': parameters['deadline'][0],
            'reward': parameters['reward'][0],
            'currency': parameters['currency'][0],
            'min_reviews': parameters['min_reviews'][0],
            'notary_signature': '0' * 64
        }

        def on_block_created(blocks):
            dappcrowd_overlay = self.get_dappcrowd_overlay()
            dappcrowd_overlay.persistence.add_app_request(blocks[0])
            request.write(json.dumps({"success": True}))
            request.finish()

        trustchain.create_source_block(block_type='dappcrowd_apprequest', transaction=tx).addCallback(on_block_created)

        return NOT_DONE_YET
