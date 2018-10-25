from twisted.web import resource


class RootEndpoint(resource.Resource):

    def __init__(self, ipv8, ipfs_api):
        resource.Resource.__init__(self)
        self.ipv8 = ipv8
        self.ipfs_api = ipfs_api

        from dappcrowd.restapi.apprequests_endpoint import AppRequestsEndpoint
        from dappcrowd.restapi.submissions_endpoint import SubmissionsEndpoint
        from dappcrowd.restapi.reviews_endpoint import ReviewsEndpoint
        self.putChild("apprequests", AppRequestsEndpoint(self.ipv8, self.ipfs_api))
        self.putChild("submissions", SubmissionsEndpoint(self.ipv8, self.ipfs_api))
        self.putChild("reviews", ReviewsEndpoint(self.ipv8, self.ipfs_api))


class DAppCrowdEndpoint(resource.Resource):

    def __init__(self, ipv8, ipfs_api):
        resource.Resource.__init__(self)
        self.ipv8 = ipv8
        self.ipfs_api = ipfs_api

    def get_trustchain(self):
        from pyipv8.ipv8.attestation.trustchain.community import TrustChainCommunity
        for overlay in self.ipv8.overlays:
            if isinstance(overlay, TrustChainCommunity):
                return overlay

    def get_dappcrowd_overlay(self):
        from dappcrowd.community import DAppCrowdCommunity
        for overlay in self.ipv8.overlays:
            if isinstance(overlay, DAppCrowdCommunity):
                return overlay
