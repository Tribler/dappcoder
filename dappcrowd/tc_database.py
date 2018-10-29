from pyipv8.ipv8.attestation.trustchain.database import TrustChainDB
from pyipv8.ipv8.database import database_blob


class DAppCrowdTrustChainDatabase(TrustChainDB):

    def get_pending_review_requests(self, public_key):
        """
        Get all pending review requests for/from a given public key.
        """
        results = []
        review_request_blocks = self._getall(u"WHERE type='dappcrowd_review_request' AND (public_key = ? OR link_public_key = ?)", (database_blob(public_key), database_blob(public_key)))
        for review_request_block in review_request_blocks:
            if not self.get_linked(review_request_block):
                results.append(review_request_block)
        return results

    def is_verified_user(self, public_key):
        """
        Return whether the user is verified or not (imported GitHub profile).
        """
        blocks = self.get_blocks_with_type(block_type='dappcrowd_github', public_key=public_key)
        return blocks is not None
