"""
This twistd plugin starts a TrustChain crawler.
"""
from __future__ import absolute_import

import os
import signal
import sys

import logging

import ipfsapi

from pyipv8.ipv8.peerdiscovery.discovery import RandomWalk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from twisted.application.service import MultiService, IServiceMaker
from twisted.internet import reactor
from twisted.plugin import IPlugin
from twisted.python import usage
from twisted.python.log import msg
from zope.interface import implements

from pyipv8.ipv8_service import IPv8
from pyipv8.ipv8.attestation.trustchain.settings import TrustChainSettings
from pyipv8.ipv8.REST.rest_manager import RESTManager

from dappcrowd.community import DAppCrowdCommunity, DAppCrowdTrustchainCommunity
from dappcrowd.restapi.root_endpoint import RootEndpoint


class Options(usage.Options):
    optParameters = [
        ["statedir", "s", ".", "Use an alternate statedir", str],
        ["port", "p", 8090, "Use an alternative port for IPv8", int],
        ["apiport", "a", 8085, "Use an alternative port for the REST api", int],
    ]
    optFlags = [
    ]


config = {
    'address': '0.0.0.0',
    'port': 8090,
    'keys': [
        {
            'alias': "my peer",
            'generation': u"medium",
            'file': u"ec.pem"
        }
    ],
    'logger': {
        'level': "ERROR"
    },
    'walker_interval': 0.5,
    'overlays': [
        {
            'class': 'DiscoveryCommunity',
            'key': "my peer",
            'walkers': [
                {
                    'strategy': "RandomWalk",
                    'peers': -1,
                    'init': {
                        'timeout': 3.0
                    }
                },
                {
                    'strategy': "RandomChurn",
                    'peers': -1,
                    'init': {
                        'sample_size': 64,
                        'ping_interval': 1.0,
                        'inactive_time': 1.0,
                        'drop_time': 3.0
                    }
                }
            ],
            'initialize': {},
            'on_start': [
                ('resolve_dns_bootstrap_addresses', )
            ]
        },
    ]
}


class DappCrowdServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "dappcrowd"
    description = "Dappcrowd service"
    options = Options

    def __init__(self):
        self.ipv8 = None
        self.ipfs_api = None
        self.restapi = None
        self._stopping = False

    def start(self, options):
        """
        Main method to startup the DAppCrowd service.
        """
        root = logging.getLogger()
        root.setLevel(logging.INFO)

        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.INFO)
        stderr_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
        root.addHandler(stderr_handler)

        if options["statedir"]:
            # If we use a custom state directory, update various variables
            for key in config["keys"]:
                key["file"] = os.path.join(options["statedir"], key["file"])

        config['port'] = options["port"]
        self.ipv8 = IPv8(config)

        # Load TrustChain + DAppCrowd community
        my_peer = self.ipv8.overlays[0].my_peer

        tc_settings = TrustChainSettings()
        tc_settings.crawler = True
        dappcrowd_tc_community = DAppCrowdTrustchainCommunity(my_peer, self.ipv8.endpoint, self.ipv8.network,
                                                              settings=tc_settings,
                                                              working_directory=options["statedir"])
        self.ipv8.overlays.append(dappcrowd_tc_community)
        self.ipv8.strategies.append((RandomWalk(dappcrowd_tc_community), 20))

        dappcrowd_community = DAppCrowdCommunity(my_peer, self.ipv8.endpoint, self.ipv8.network)
        self.ipv8.overlays.append(dappcrowd_community)
        self.ipv8.strategies.append((RandomWalk(dappcrowd_community), 20))

        def signal_handler(sig, _):
            msg("Received shut down signal %s" % sig)
            if not self._stopping:
                self._stopping = True
                if self.restapi:
                    self.restapi.stop()
                self.ipv8.stop()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        msg("Starting DAppCrowd")

        self.ipfs_api = ipfsapi.connect('127.0.0.1', 5001)

        self.restapi = RESTManager(self.ipv8)
        self.restapi.start(options["apiport"])
        self.restapi.root_endpoint.putChild("dappcrowd", RootEndpoint(self.ipv8, self.ipfs_api))

    def makeService(self, options):
        """
        Construct a IPv8 service.
        """
        crawler_service = MultiService()
        crawler_service.setName("DAppCrowd")

        reactor.callWhenRunning(self.start, options)

        return crawler_service


service_maker = DappCrowdServiceMaker()
