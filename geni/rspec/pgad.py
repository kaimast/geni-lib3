# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from lxml import etree as ET

import geni.namespaces as GNS
from geni.rspec.pg import Namespaces as PGNS

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name}

class AdNode(object):
  def __init__ (self):
    self.component_id = None
    self.name = None
    self.exclusive = True
    self.available = False
    self.hardware_types = set()
    self.sliver_types = set()
    self.shared = False

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
      node.hardware_types.add(htype.get("name"))

    fds = elem.xpath('e:fd', namespaces = _XPNS)
    for fd in fds:
      name = fd.get("name")
      if name == 'pcshared':
        node.shared = True
      elif name == 'cpu':
        node.cpu = fd.get("weight")
      elif name == 'ram':
        node.ram = fd.get("ram")

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
  def __init__ (self, path):
    self._root = ET.parse(open(path))

  @property
  def nodes (self):
    for node in self._root.findall("{%s}node" % (GNS.REQUEST.name)):
      yield AdNode._fromdom(node)

  @property
  def shared_vlans (self):
    for vlan in self._root.xpath('/g:rspec/s:rspec_shared_vlan/s:available', namespaces = _XPNS):
      yield AdSharedVLAN._fromdom(vlan)
