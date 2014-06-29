# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import os

from lxml import etree as ET

import geni.namespaces as GNS

XPNS = {'g' : GNS.REQUEST.name,
        'v' : "http://geni.bssoftworks.com/rspec/ext/vts/manifest/1",
        's' : "http://geni.bssoftworks.com/rspec/ext/sdn/manifest/1"}

class Manifest(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._xml = open(path, "r").read()
    elif xml:
      self._xml = xml
    self._root = ET.fromstring(self._xml)
    self._pid = os.getpid()
  
  @property
  def root (self):
    if os.getpid() != self._pid:
      self._root = ET.fromstring(self._xml)
      self._pid = os.getpid()
    return self._root

  @property
  def text (self):
    return ET.tostring(self.root, pretty_print=True)

  @property
  def pg_circuits (self):
    elems = self._root.xpath("v:datapath/v:port[@shared_lan]", namespaces = XPNS)
    for elem in elems:
      yield elem.get("shared_lan")
