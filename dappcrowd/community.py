from binascii import unhexlify

from dappcrowd.database import DAppCrowdDatabase
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


class DAppCrowdCommunity(Community, BlockListener):

    master_peer = Peer(unhexlify('3081a7301006072a8648ce3d020106052b81040027038192000406297d96eafe1f25408ecc44062310'
                                 '67d4d644bf837e051d64fee582788544b360d30f21004eeb7f3425331423c7d5c9cc56ad7358558a43'
                                 '6fd46ac53dc9f25575f4b28a512c8ca002aaab6d820800634f009a8d509e600a9c7f9a171e9d0c3a66'
                                 'd2a823a5f6d6d2bfb5d96c1725163b03242a1e6b7d51ae110d5666d696640f4e3633bd9da346397dcd'
                                 '0dd47bd6fe29'))

    def __init__(self, *args, **kwargs):
        working_directory = kwargs.pop('working_directory', '')
        super(DAppCrowdCommunity, self).__init__(*args, **kwargs)

        self.persistence = DAppCrowdDatabase(working_directory, 'dappcrowd')

    def should_sign(self, block):
        return True

    def received_block(self, block):
        pass

    def unload(self):
        super(DAppCrowdCommunity, self).unload()

        # Close the persistence layer
        self.persistence.close()