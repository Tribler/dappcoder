import json

from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class GithubEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.putChild("import", GithubImportEndpoint(ipv8, ipfs_api))


class GithubImportEndpoint(DAppCrowdEndpoint):

    def render_PUT(self, request):
        """
        Import your Github account into DAppCrowd.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        if 'username' not in parameters:
            request.setResponseCode(http.BAD_REQUEST)
            return json.dumps({"error": "missing username parameter"})

        username = parameters['username'][0]

        def on_block_created(_):
            request.write(json.dumps({"success": True}))
            request.finish()

        def on_error(failure):
            request.setResponseCode(http.UNAUTHORIZED)
            request.write(json.dumps({"error": failure.getErrorMessage()}))
            request.finish()

        self.get_dappcrowd_overlay().import_github_profile(username).addCallbacks(on_block_created, on_error)

        return NOT_DONE_YET