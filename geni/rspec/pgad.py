# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

import geni.namespaces as GNS
from geni.rspec.pg import Namespaces as PGNS
from geni.rspec import pg
from geni.model.util import XPathXRange

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name}

class Image(object):
  def __init__ (self):
    self.name = None
    self.os = None
    self.version = None
    self.description = None
    self.url = None

  def __repr__ (self):
    return "<Image: %s, os: '%s', version: '%s', description: '%s', url: '%s'>" % (self.name, self.os, self.version, self.description, self.url)

  @classmethod
  def _fromdom (self, elem):
    i = Image()
    i.name = elem.get("name")
    if i.name is None:
      i.name = elem.get("url")
    i.os = elem.get("os")
    i.version = elem.get("version")
    i.description = elem.get("description")
    i.url = elem.get("url")
    return i

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
    name = elem.get("component_id")
    if len(eie) > 0:
      name = eie[0].get("name")
    intf = AdInterface(name)

    intf.component_id = elem.get("component_id")
    intf.role = elem.get("role")

    return intf


class AdNode(object):
  def __init__ (self):
    self.component_id = None
    self.component_manager_id = None
    self.name = None
    self.exclusive = True
    self.available = False
    self.hardware_types = {}
    self.sliver_types = set()
    self.images = {}
    self.shared = False
    self.interfaces = []
    self.location = None

  @classmethod
  def _fromdom (cls, elem):
    node = AdNode()
    node.component_id = elem.get("component_id")
    node.name = elem.get("component_name")
    node.component_manager_id = elem.get("component_manager_id")
    if elem.get("exclusive") == "false":
      node.exclusive = False

    avelem = elem.xpath('g:available', namespaces = _XPNS)
    if avelem and avelem[0].get("now") == "true":
      node.available = True

    stypes = elem.xpath('g:sliver_type', namespaces = _XPNS)
    for stype in stypes:
      sliver_name = stype.get("name")
      node.sliver_types.add(sliver_name)
      node.images[sliver_name] = []
      ims = stype.xpath('g:disk_image', namespaces = _XPNS)
      for im in ims:
        node.images[sliver_name].append(Image._fromdom(im))

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

class AdLink(object):
  def __init__ (self):
    self.component_id = None
    self.link_types = set()

  @classmethod
  def _fromdom (cls, elem):
    link = AdLink()
    link.component_id = elem.get("component_id")
    
    ltypes = elem.xpath('g:link_type', namespaces = _XPNS)
    for ltype in ltypes:
      link.link_types.add(ltype.get("name"))

    return link

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


class RoutableAddresses(object):
  def __init__ (self):
    self.available = 0
    self.configured = 0

  @property
  def capacity (self):
    return self.configured


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)
    self._routable_addresses = None

  def _parse_routable (self):
    try:
      elem = self._root.xpath('/g:rspec/e:rspec_routable_addresses', namespaces=_XPNS)[0]
      ra = RoutableAddresses()
      ra.available = int(elem.get("available"))
      ra.configured = int(elem.get("configured"))
      self._routable_addresses = ra
    except Exception, e:
      pass
    
  @property
  def routable_addresses (self):
    if not self._routable_addresses:
      self._parse_routable()
    return self._routable_addresses

  @property
  def nodes (self):
    return XPathXRange(self._root.findall("{%s}node" % (GNS.REQUEST.name)), AdNode)

  @property
  def links (self):
    return XPathXRange(self._root.findall("{%s}link" % (GNS.REQUEST.name)), AdLink)

  @property
  def shared_vlans (self):
    return XPathXRange(self._root.xpath('/g:rspec/s:rspec_shared_vlan/s:available', namespaces=_XPNS), AdSharedVLAN)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
