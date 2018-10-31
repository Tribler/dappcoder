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
