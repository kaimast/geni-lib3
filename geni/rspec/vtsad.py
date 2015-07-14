# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import geni.namespaces as GNS
from geni.model.util import XPathXRange

from lxml import etree as ET

VTSNS = GNS.Namespace("vts", "http://geni.bssoftworks.com/rspec/ext/vts/ad/1")
_XPNS = {'g' : GNS.REQUEST.name, 'v' : VTSNS.name}

class CircuitPlane(object):
  def __init__ (self):
    self.label = None
    self.mtu = None
    self.type = None
    self.endpoint = None
    self.tunnel_types = []

  @classmethod
  def _fromdom (cls, elem):
    cp = CircuitPlane()
    cp.label = elem.get("label")
    cp.mtu = int(elem.get("mtu"))
    supported = elem.xpath('v:supported-tunnels/v:tunnel-type', namespaces = _XPNS)
    for tuntyp in supported:
      cp.tunnel_types.append(tuntyp.get("name"))
    cp.endpoint = elem.xpath('v:endpoint', namespaces = _XPNS)[0].get("value")
    return cp


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def circuit_planes (self):
    return XPathXRange(self._root.xpath("v:circuit-planes/v:circuit-plane", namespaces = _XPNS), CircuitPlane)
    
  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
