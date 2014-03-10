# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

import geni.namespaces as GNS
from geni.rspec.pg import Namespaces as PGNS
from geni.rspec import pg
from geni.model.util import XPathXRange

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name}


class Location(object):
  def __init__ (self):
    self.latitude = None
    self.longitude = None

  def __repr__ (self):
    return "<Location: %f, %f>" % (self.latitude, self.longitude)

  @classmethod
  def _fromdom (self, elem):
    l = Location()
    l.latitude = float(elem.get("latitude"))
    l.longitude = float(elem.get("longitude"))
    return l


class AdInterface(pg.Interface):
  def __init__ (self, name):
    super(AdInterface, self).__init__(name, None)
    self.component_id = None
    self.role = None
    self.addresses = []

  @classmethod
  def _fromdom (cls, elem):
    eie = elem.xpath('e:interface', namespaces = _XPNS)
    intf = AdInterface(eie[0].get("name"))

    intf.component_id = elem.get("component_id")
    intf.role = elem.get("role")

    return intf


class AdNode(object):
  def __init__ (self):
    self.component_id = None
    self.name = None
    self.exclusive = True
    self.available = False
    self.hardware_types = {}
    self.sliver_types = set()
    self.shared = False
    self.interfaces = []
    self.location = None

  @classmethod
  def _fromdom (cls, elem):
    node = AdNode()
    node.component_id = elem.get("component_id")
    node.name = elem.get("component_name")
    if elem.get("exclusive") == "false":
      node.exclusive = False

    avelem = elem.xpath('g:available', namespaces = _XPNS)
    if avelem and avelem[0].get("now") == "true":
      node.available = True

    stypes = elem.xpath('g:sliver_type', namespaces = _XPNS)
    for stype in stypes:
      node.sliver_types.add(stype.get("name"))

    htypes = elem.xpath('g:hardware_type', namespaces = _XPNS)
    for htype in htypes:
      nts = htype.xpath('e:node_type', namespaces = _XPNS)
      node.hardware_types[htype.get("name")] = nts[0].get("type_slots")

    fds = elem.xpath('e:fd', namespaces = _XPNS)
    for fd in fds:
      name = fd.get("name")
      if name == 'pcshared':
        node.shared = True
      elif name == 'cpu':
        node.cpu = fd.get("weight")
      elif name == 'ram':
        node.ram = fd.get("weight")

    for intf in elem.xpath('g:interface', namespaces = _XPNS):
      node.interfaces.append(AdInterface._fromdom(intf))

    locelem = elem.xpath('g:location', namespaces = _XPNS)
    if locelem:
      node.location = Location._fromdom(locelem[0])

    return node


class AdSharedVLAN(object):
  def __init__ (self):
    self.name = None

  def __str__ (self):
    return self.name

  @classmethod
  def _fromdom (cls, elem):
    svlan = AdSharedVLAN()
    svlan.name = elem.get("name")
    return svlan


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def nodes (self):
    return XPathXRange(self._root.findall("{%s}node" % (GNS.REQUEST.name)), AdNode)

  @property
  def shared_vlans (self):
    return XPathXRange(self._root.xpath('/g:rspec/s:rspec_shared_vlan/s:available', namespaces=_XPNS), AdSharedVLAN)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
