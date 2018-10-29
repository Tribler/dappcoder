from binascii import unhexlify

import requests
from twisted.internet.defer import fail

from dappcrowd.database import DAppCrowdDatabase
from dappcrowd.tc_database import DAppCrowdTrustChainDatabase
from pyipv8.ipv8.attestation.trustchain.community import TrustChainCommunity
from pyipv8.ipv8.attestation.trustchain.listener import BlockListener
from pyipv8.ipv8.deprecated.community import Community
from pyipv8.ipv8.peer import Peer


class DAppCrowdTrustchainCommunity(TrustChainCommunity):
    master_peer = Peer(unhexlify('3081a7301006072a8648ce3d020106052b81040027038192000404267964a5be4a43ee1e59397c6765'
                                 '8db0dadc276a89163a3b1f7dec3fdb4cecd94dd80968c9983bfffcd2cd58e8ec7ada6dded7ff3b389b'
                                 '85f691ee0e7981326b4b4deb80ad536801d781795a335f501b80c00b479f076f0384fa7fa3bd940f76'
                                 '82840dae77d46f938f49743acb5d2ab723046982608d60f2398853f9898d97e4e3b35fa19eb92f0ba2'
                                 'c1570a31ae72'))
    DB_CLASS = DAppCrowdTrustChainDatabase


class DAppCrowdCommunity(Community, BlockListener):

    master_peer = Peer(unhexlify('3081a7301006072a8648ce3d020106052b81040027038192000406297d96eafe1f25408ecc44062310'
                                 '67d4d644bf837e051d64fee582788544b360d30f21004eeb7f3425331423c7d5c9cc56ad7358558a43'
                                 '6fd46ac53dc9f25575f4b28a512c8ca002aaab6d820800634f009a8d509e600a9c7f9a171e9d0c3a66'
                                 'd2a823a5f6d6d2bfb5d96c1725163b03242a1e6b7d51ae110d5666d696640f4e3633bd9da346397dcd'
                                 '0dd47bd6fe29'))

    def __init__(self, *args, **kwargs):
        working_directory = kwargs.pop('working_directory', '')
        self.trustchain = kwargs.pop('trustchain')
        super(DAppCrowdCommunity, self).__init__(*args, **kwargs)

        self.persistence = DAppCrowdDatabase(working_directory, 'dappcrowd')

        self.trustchain.add_listener(self, ['dappcrowd_review_request'])

    def should_sign(self, block):
        if block.type == 'dappcrowd_review_request':
            return False  # We counter-sign this one manually
        return True

    def received_block(self, block):
        pass

    def request_review(self, submission_id, requester_pub_key):
        """
        Request a review for a submission from another peer.
        """
        tx = {
            'submission_id': submission_id
        }

        peer = self.network.get_verified_by_public_key_bin(requester_pub_key)
        self.trustchain.sign_block(peer, requester_pub_key, block_type='dappcrowd_review_request', transaction=tx)

    def respond_to_review_request(self, block_hash, accept):
        """
        Accept/reject a review request for a given block hash
        """
        block = self.trustchain.persistence.get_block_with_hash(block_hash)
        peer = self.network.get_verified_by_public_key_bin(block.public_key)
        self.trustchain.sign_block(peer, linked=block, additional_info={'accept': accept})

    def get_github_profile(self, username):
        """
        Get the GitHub profile for a given username.
        """
        return requests.get("https://api.github.com/users/%s" % username).json()

    def import_github_profile(self, username):
        """
        Import your GitHub profile.
        """
        profile_info = self.get_github_profile(username)
        mid = self.trustchain.my_peer.mid.encode('hex')
        if not profile_info['bio'] or mid not in profile_info['bio']:
            return fail(RuntimeError("your member ID (%s) should be in the GitHub bio!" % mid))

        # Challenge successful, create TrustChain block
        tx = {
            'username': username,
            'followers': profile_info['followers']
        }

        self.trustchain.create_source_block(block_type='dappcrowd_github', transaction=tx)

    def unload(self):
        super(DAppCrowdCommunity, self).unload()

        # Close the persistence layer
        self.persistence.close()
