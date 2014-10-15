# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import os

from lxml import etree as ET

import geni.namespaces as GNS

XPNS = {'g' : GNS.REQUEST.name,
        'v' : "http://geni.bssoftworks.com/rspec/ext/vts/manifest/1",
        's' : "http://geni.bssoftworks.com/rspec/ext/sdn/manifest/1"}

class UnhandledPortTypeError(Exception):
  def __init__ (self, typ):
    self.typ = typ
  def __str__ (self):
    return "Port type '%s' isn't supported by port builder.  Perhaps you should contribute some code?"


class GREPort(object):
  def __init__ (self):
    self.client_id = None
    self.circuit_plane = None
    self.local_endpoint = None
    self.remote_endpoint = None

  @classmethod
  def _fromdom (cls, elem):
    p = GREPort()
    p.client_id = elem.get("client_id")
    endpe = elem.xpath("v:endpoint", namespaces=XPNS)[0]
    p.circuit_plane = endpe.get("circuit-plane")
    p.local_endpoint = endpe.get("local")
    p.remote_endpoint = endpe.get("remote")
    return p
    

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

  def findPort (self, client_id):
    pelems = self._root.xpath("v:datapath/v:port[@client_id='%s']" % (client_id), namespaces = XPNS)
    if pelems:
      return self._buildPort(pelems[0])

  def _buildPort (self, elem):
    t = elem.get("type")
    if t == "gre":
      return GREPort._fromdom(elem)
    raise UnhandledPortTypeError(t)

  def write (self, path):
    f = open(path, "w+")
    f.write(ET.tostring(self.root, pretty_print=True))
    f.close()
