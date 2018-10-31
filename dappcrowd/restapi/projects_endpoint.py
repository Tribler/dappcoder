import json

from twisted.web import http
from twisted.web.server import NOT_DONE_YET

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class ProjectsEndpoint(DAppCrowdEndpoint):

    def render_GET(self, request):
        """
        Get all projects
        """
        dappcrowd_overlay = self.get_dappcrowd_overlay()
        return json.dumps({"projects": dappcrowd_overlay.persistence.get_projects()})

    def getChild(self, path, request):
        return ProjectPKEndpoint(self.ipv8, self.ipfs_api, path)

    def render_PUT(self, request):
        """
        Initiate a new project.
        """
        parameters = http.parse_qs(request.content.read(), 1)
        required_params = ['name', 'specifications', 'deadline', 'reward', 'currency', 'min_reviews']
        for required_param in required_params:
            if required_param not in parameters:
                request.setResponseCode(http.BAD_REQUEST)
                return json.dumps({"error": "missing parameter %s" % required_param})

        # TODO: notary signature! Contact third-party provider...
        # TODO add tests

        def on_block_created(blocks):
            request.write(json.dumps({"success": True}))
            request.finish()

        self.get_dappcrowd_overlay().create_project(parameters['name'][0], parameters['specifications'][0],
                                                    parameters['deadline'][0], parameters['reward'][0],
                                                    parameters['currency'][0], parameters['min_reviews'][0]).addCallback(on_block_created)

        return NOT_DONE_YET


class ProjectPKEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key.decode('hex')

    def getChild(self, path, request):
        return SpecificProjectEndpoint(self.ipv8, self.ipfs_api, self.public_key, path)


class SpecificProjectEndpoint(DAppCrowdEndpoint):

    def __init__(self, ipv8, ipfs_api, public_key, project_id):
        DAppCrowdEndpoint.__init__(self, ipv8, ipfs_api)
        self.public_key = public_key
        self.project_id = project_id

    def render_GET(self, request):
        if not self.get_dappcrowd_overlay().persistence.has_project(self.public_key, self.project_id):
            request.setResponseCode(http.NOT_FOUND)
            return json.dumps({"error": "the project is not found"})

        return json.dumps({
            "project": self.get_dappcrowd_overlay().persistence.get_project(self.public_key, self.project_id)
        })
