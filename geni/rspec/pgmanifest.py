# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET
from geni.rspec.pg import Link
import geni.namespaces as GNS
from geni.rspec.pg import Namespaces as PGNS

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name}

class ManifestLink(Link):
  def __init__ (self):
    super(ManifestLink, self).__init__()

  @classmethod
  def _fromdom (cls, elem):
    lnk = ManifestLink()
    lnk.client_id = elem.get("client_id")
    lnk.sliver_id = elem.get("sliver_id")
    lnk.vlan = elem.get("vlantag", None)

    return lnk


class ManifestNode(object):
  class Login(object):
    def __init__ (self):
      self.auth = None
      self.hostname = None
      self.port = None
      self.username = None

  class Interface(object):
    def __init__ (self):
      self.client_id = None
      self.mac_address = None
      self.sliver_id = None
      self.address_info = None

  def __init__ (self):
    super(ManifestNode, self).__init__()
    self.logins = []
    self.interfaces = []
    self.name = None

  @classmethod
  def _fromdom (cls, elem):
    n = ManifestNode()
    n.name = elem.get("client_id")

    logins = elem.xpath('g:services/g:login', namespaces = _XPNS)
    for lelem in logins:
      l = ManifestNode.Login()
      l.auth = lelem.get("authentication")
      l.hostname = lelem.get("hostname")
      l.port = int(lelem.get("port"))
      l.username = lelem.get("username")
      n.logins.append(l)

    interfaces = elem.xpath('g:interface', namespaces = _XPNS)
    for ielem in interfaces:
      i = ManifestNode.Interface()
      i.client_id = ielem.get("client_id")
      i.sliver_id = ielem.get("sliver_id")
      i.mac_address = ielem.get("mac_address")
      try:
        ipelem = ielem.xpath('g:ip', namespaces = _XPNS)[0]
        self.address_info = (ipelem.get("address"), ipelem.get("netmask"))
      n.interfaces.append(i)

    return n


class Manifest(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def links (self):
    for link in self._root.findall("{%s}link" % (GNS.REQUEST.name)):
      yield ManifestLink._fromdom(link)

  @property
  def nodes (self):
    for node in self._root.findall("{%s}node" % (GNS.REQUEST.name)):
      yield ManifestNode._fromdom(node)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
