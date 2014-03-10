# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

import geni.namespaces as GNS
from .pgad import Location

TOPO = GNS.Namespace("topo", "http://geni.bssoftworks.com/rspec/ext/topo/1")

XPNS = {'g' : GNS.REQUEST.name, 'o' : GNS.OFv3.name, 't' : TOPO.name}

class Port(object):
  def __init__ (self):
    self.name = None
    self.number = None

  def __repr__ (self):
    return "<Port %s,%s>" % (self.name, self.number)

  @classmethod
  def _fromdom (cls, elem):
    p = Port()
    p.name = elem.get("name")
    p.number = elem.get("number")


class Datapath(object):
  def __init__ (self):
    self.dpid = None
    self.component_id = None
    self.ports = []
    self.location = None

  @classmethod
  def _fromdom (cls, elem):
    d = Datapath()
    d.dpid = elem.get("dpid")
    d.component_id = elem.get("component_id")

    ports = elem.xpath('o:port', namespaces = XPNS)
    for pelem in ports:
      d.ports.append(Port._fromdom(pelem))

    lelem = elem.xpath('o:location', namespaces = XPNS)
    if lelem:
      d.location = Location._fromdom(lelem[0])
      
    return d


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)

  @property
  def datapaths (self):
    for datapath in self._root.findall("{%s}datapath" % (GNS.OFv3.name)):
      yield Datapath._fromdom(datapath)
