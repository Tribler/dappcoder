from pyipv8.ipv8.attestation.trustchain.database import TrustChainDB
from pyipv8.ipv8.database import database_blob


class DAppCrowdTrustChainDatabase(TrustChainDB):

    def __init__(self, working_directory, db_name):
        super(DAppCrowdTrustChainDatabase, self).__init__(working_directory, db_name)
        self.my_peer = None

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
        blocks = self.get_blocks_with_type(block_type='devid_connection', public_key=public_key)
        return len(blocks) > 0

    def get_username(self, public_key):
        """
        Return the username of a given public key, or unknown if he/she did not import an existing profile.
        """
        blocks = self.get_blocks_with_type(block_type='devid_connection', public_key=public_key)
        if not blocks:
            return 'unknown'
        return blocks[0].transaction['info']['username']

    def get_detailled_user_info(self, public_key):
        """
        Return a dictionary that contains information about a specific user.
        """
        github_info = None
        bitbucket_info = None

        imported_profiles_blocks = self.get_blocks_with_type(block_type='devid_connection', public_key=public_key)
        if imported_profiles_blocks:
            for profile_block in imported_profiles_blocks:
                if profile_block.transaction['platform'] == 'github' and not github_info:
                    github_info = profile_block.transaction['info']
                # TODO BITBUCKET

        return {
            "public_key": public_key.encode('hex'),
            "verified": self.is_verified_user(public_key),
            "username": self.get_username(public_key),
            "skills": self.get_skills(public_key),
            "github_info": github_info,
            "bitbucket_info": bitbucket_info,
            "mid": self.my_peer.mid.encode('hex')
        }

    def get_users_list(self):
        """
        Return a list with information about all known users in the system.
        """
        user_dicts = []
        pub_keys = list(self.execute("SELECT DISTINCT public_key FROM blocks"))
        for tup_item in pub_keys:
            pub_key = str(tup_item[0])
            user_dicts.append({
            "public_key": pub_key.encode('hex'),
            "verified": self.is_verified_user(pub_key),
            "username": self.get_username(pub_key),
        })
        return user_dicts

    def get_num_endorsements(self, skill_block):
        """
        Get the number of endorsements for a given skill block
        """
        return len(self._getall("WHERE type='devid_skill' AND link_public_key = ? AND link_sequence_number = ?", (database_blob(skill_block.public_key), skill_block.sequence_number)))

    def did_endorse_skill(self, skill_block):
        """
        Return whether you endorsed this skill already or not
        """
        if skill_block.public_key == self.my_peer.public_key.key_to_bin():
            return True

        return len(self._getall("WHERE type='devid_skill' AND public_key =? AND link_public_key = ? AND link_sequence_number = ?",
                                (database_blob(self.my_peer.public_key.key_to_bin()), database_blob(skill_block.public_key), skill_block.sequence_number))) > 0

    def get_skills(self, public_key):
        """
        Get all skills of a specific user.
        """
        skills_list = []
        skill_blocks = self._getall("WHERE type='devid_skill' AND public_key = ? AND link_sequence_number = 0", (database_blob(public_key),))
        for skill_block in skill_blocks:
            skills_list.append({
                "name": skill_block.transaction['name'],
                "block_num": skill_block.sequence_number,
                "endorsements": self.get_num_endorsements(skill_block),
                "did_endorse": self.did_endorse_skill(skill_block)
            })
        return skills_list
