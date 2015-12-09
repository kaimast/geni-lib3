# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import os

from lxml import etree as ET

from geni.rspec.pg import Link
import geni.namespaces as GNS
from geni.rspec.pg import Namespaces as PGNS

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name}

class ManifestLink(Link):
  def __init__ (self):
    super(ManifestLink, self).__init__()
    self.interface_refs = []

  @classmethod
  def _fromdom (cls, elem):
    lnk = ManifestLink()
    lnk.client_id = elem.get("client_id")
    lnk.sliver_id = elem.get("sliver_id")
    lnk.vlan = elem.get("vlantag", None)

    refs = elem.xpath('g:interface_ref', namespaces = _XPNS)
    for ref in refs:
      lnk.interface_refs.append(ref.get("sliver_id"))

    svlans = elem.xpath('s:link_shared_vlan', namespaces = _XPNS)
    if svlans:
      # TODO: Can a link be attached to more than one shared vlan?
      # Don't believe PG supports trunks, but the rspec doesn't really forbid it
      lnk.vlan = svlans[0].get("name")

    return lnk

class ManifestSvcLogin(object):
  def __init__ (self):
    self.auth = None
    self.hostname = None
    self.port = None
    self.username = None

  @classmethod
  def _fromdom (cls, elem):
    n = ManifestSvcLogin()
    n.auth = elem.get("authentication")
    n.hostname = elem.get("hostname")
    n.port = int(elem.get("port"))
    n.username = elem.get("username")

    return n


class ManifestNode(object):
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
    self.component_id = None
    self.sliver_id = None

  @classmethod
  def _fromdom (cls, elem):
    n = ManifestNode()
    n.name = elem.get("client_id")
    n.component_id = elem.get("component_id")
    n.sliver_id = elem.get("sliver_id")

    logins = elem.xpath('g:services/g:login', namespaces = _XPNS)
    for lelem in logins:
      l = ManifestSvcLogin._fromdom(lelem)
      n.logins.append(l)

    interfaces = elem.xpath('g:interface', namespaces = _XPNS)
    for ielem in interfaces:
      i = ManifestNode.Interface()
      i.client_id = ielem.get("client_id")
      i.sliver_id = ielem.get("sliver_id")
      i.component_id = ielem.get("component_id")
      i.mac_address = ielem.get("mac_address")
      try:
        ipelem = ielem.xpath('g:ip', namespaces = _XPNS)[0]
        i.address_info = (ipelem.get("address"), ipelem.get("netmask"))
      except Exception, e:
        pass
      n.interfaces.append(i)

    return n


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
  def links (self):
    for link in self.root.findall("{%s}link" % (GNS.REQUEST.name)):
      yield ManifestLink._fromdom(link)

  @property
  def nodes (self):
    for node in self.root.findall("{%s}node" % (GNS.REQUEST.name)):
      yield ManifestNode._fromdom(node)

  @property
  def text (self):
    return ET.tostring(self.root, pretty_print=True)

  def write (self, path):
    """
.. deprecated:: 0.4
    Use :py:meth:`geni.rspec.pg.Request.writeXML` instead."""

    import geni.warnings as GW
    import warnings
    warnings.warn("The Manifest.write() method is deprecated, please use Manifest.writeXML() instead",
                  GW.GENILibDeprecationWarning, 2)
    self.writeXML(path)

  def writeXML (self, path):
    """Write the current manifest as an XML file that contains an rspec in the format returned by the
    aggregate."""
    f = open(path, "w+")
    f.write(ET.tostring(self.root, pretty_print=True))
    f.close()
