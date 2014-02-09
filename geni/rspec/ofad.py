# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from lxml import etree as ET

import geni.namespaces as GNS

class Datapath(object):
  def __init__ (self):
    self.dpid = None
    self.component_id = None

  @classmethod
  def _fromdom (cls, elem):
    d = Datapath()
    d.dpid = elem.get("dpid")
    d.component_id = elem.get("component_id")
    return d


class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def datapaths (self):
    for datapath in self._root.findall("{%s}datapath" % (GNS.OFv3.name)):
      yield AdDatapath._fromdom(datapath)
