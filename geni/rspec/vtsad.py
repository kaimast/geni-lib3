# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET

import geni.namespaces as GNS
from geni.model.util import XPathXRange


VTSNS = GNS.Namespace("vts", "http://geni.bssoftworks.com/rspec/ext/vts/ad/1")
_XPNS = {'g' : GNS.REQUEST.name, 'v' : VTSNS.name}

def dumbcoerce (val):
  try:
    return int(val)
  except Exception:
    pass

  if val.lower() == "true": return True
  if val.lower() == "false": return False

  return val


class CircuitPlane(object):
  def __init__ (self):
    self.label = None
    self.type = None
    self.endpoint = None
    self.tunnel_types = []
    self.constraints = {}

  @classmethod
  def _fromdom (cls, elem):
    cp = CircuitPlane()
    cp.label = elem.get("label")
    supported = elem.xpath('v:supported-tunnels/v:tunnel-type', namespaces = _XPNS)
    for tuntyp in supported:
      cp.tunnel_types.append(tuntyp.get("name"))
    cp.endpoint = elem.xpath('v:endpoint', namespaces = _XPNS)[0].get("value")
    for celem in elem.xpath('v:contraints/v:constraint', namespaces = _XPNS):
      self.constraints[celem.get("key")] = dumbcoerce(celem.get("value"))
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
