from twisted.internet.defer import inlineCallbacks

from dappcrowd.community import DAppCrowdCommunity, DAppCrowdTrustchainCommunity
from pyipv8.ipv8.test.base import TestBase
from pyipv8.ipv8.test.mocking.ipv8 import MockIPv8


class TestDAppCrowdCommunity(TestBase):

    def setUp(self):
        super(TestDAppCrowdCommunity, self).setUp()
        self.initialize(DAppCrowdCommunity, 2)

    def create_node(self):
        return MockIPv8(u"curve25519", DAppCrowdCommunity, working_directory=u":memory:", create_trustchain=True,
                        trustchain_class=DAppCrowdTrustchainCommunity)

    @inlineCallbacks
    def test_request_review(self):
        """
        Test requesting a review from another party and accepting/rejecting it
        """
        other_pk = self.nodes[1].overlay.my_peer.public_key.key_to_bin()
        self.nodes[0].overlay.request_review(1, other_pk)
        yield self.deliver_messages()

        pending_review_requests = self.nodes[1].overlay.trustchain.persistence.get_pending_review_requests(other_pk)
        self.assertTrue(pending_review_requests)

        self.nodes[1].overlay.respond_to_review_request(pending_review_requests[0].hash, True)
        yield self.deliver_messages()

        pending_review_requests = self.nodes[1].overlay.trustchain.persistence.get_pending_review_requests(other_pk)
        self.assertFalse(pending_review_requests)
        self.assertEqual(self.nodes[0].overlay.trustchain.persistence.get_number_of_known_blocks(), 2)

    @inlineCallbacks
    def test_verified_user(self):
        """
        Test whether a user is correctly verified in the system
        """
        self.nodes[0].overlay.trustchain.get_github_profile = lambda username: {
            "username": username,
            "bio": self.nodes[0].overlay.my_peer.mid.encode('hex'),
            "followers": 1337
        }
        yield self.nodes[0].overlay.trustchain.import_github_profile("test")
        yield self.deliver_messages()

        self.assertTrue(self.nodes[1].overlay.trustchain.persistence.is_verified_user(self.nodes[0].overlay.my_peer.public_key.key_to_bin()))

    @inlineCallbacks
    def test_skills(self):
        """
        Test creating a skill and endorsing another user
        """
        yield self.nodes[0].overlay.trustchain.add_skill('test')
        yield self.deliver_messages()
        peer1_pub_key = self.nodes[0].overlay.trustchain.my_peer.public_key.key_to_bin()
        self.assertTrue(self.nodes[0].overlay.trustchain.persistence.get_skills(peer1_pub_key))

        skills = self.nodes[1].overlay.trustchain.persistence.get_skills(peer1_pub_key)
        self.assertTrue(skills)

        # Peer 2 endorses peer 1 now
        block, _ = yield self.nodes[1].overlay.trustchain.endorse_skill(peer1_pub_key, skills[0]['block_num'])
        yield self.deliver_messages()
        self.assertTrue(self.nodes[1].overlay.trustchain.persistence.did_endorse_skill(block))

        skills = self.nodes[0].overlay.trustchain.persistence.get_skills(peer1_pub_key)
        self.assertEqual(skills[0]['endorsements'], 1)
