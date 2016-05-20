from __future__ import absolute_import

from ..pg import LAN, Request
from .epcexc import InvalidRequestRSpec, UnboundRSpec
from .pndefs import EPCLANS

#
# EPC lan class.  Convenience wrapper.
#
class EPClan(LAN):
    _lans = {}
    _rspec = None
    _vmlans = 0

    def __init__(self, name, linkbw = 0, usevmlans = 0):
        super(EPClan, self).__init__(name)
        if linkbw == 0:
            self.best_effort = 1
        else:
            self.bandwidth = linkbw
        if EPClan._vmlans or usevmlans:
            self.vlan_tagging = 1
            self.trivial_ok = 1
            self.link_multiplexing = 1

    @classmethod
    def usevmlans(klass, onoff):
        klass._vmlans = onoff

    @classmethod
    def bindRSpec(klass, rspec):
        if type(rspec) != Request:
            raise InvalidRequestRSpec()
        klass._rspec = rspec

    @classmethod
    def addToLAN(klass, lan, node, bandwidth = 0, latency = 0):
        if not klass._rspec:
            raise UnboundRSpec()
        if not lan in klass._lans:
            klass._lans[lan] = klass(lan)
            # Don't ever shape the management LAN.
            if lan == EPCLANS.MGMT:
                klass._lans[lan].bandwidth = -1
                klass._lans[lan].best_effort = 1
                bandwidth = 0
                latency = 0
            klass._rspec.addResource(klass._lans[lan])
        if not klass._lans[lan].isMember(node):
            return klass._lans[lan].addMember(node, bandwidth, latency)

    def isMember(self, node):
        for intf in self.interfaces:
            if intf.node == node:
                return True
        return False

    def addMember(self, node, bandwidth = 0, latency = 0):
        intf = node.addInterface(self.client_id)
        if bandwidth:
            intf.bandwidth = bandwidth
        if latency:
            intf.latency = latency
        self.addInterface(intf)
        return intf
