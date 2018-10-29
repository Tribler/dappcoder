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
        blocks = self.get_blocks_with_type(block_type='dappcrowd_connection', public_key=public_key)
        return blocks is not None

    def get_username(self, public_key):
        """
        Return the username of a given public key, or unknown if he/she did not import an existing profile.
        """
        blocks = self.get_blocks_with_type(block_type='dappcrowd_connection', public_key=public_key)
        if not blocks:
            return 'unknown'
        return blocks[0].transaction['username']

    def get_users_dict(self):
        """
        Return a dictionary with information about all known users in the system.
        """
        user_dicts = []
        pub_keys = list(self.execute("SELECT DISTINCT public_key FROM blocks"))
        for tup_item in pub_keys:
            pub_key = str(tup_item[0])
            user_dicts.append({
                "public_key": pub_key.encode('hex'),
                "verified": self.is_verified_user(pub_key),
                "username": self.get_username(pub_key)
            })
        return user_dicts