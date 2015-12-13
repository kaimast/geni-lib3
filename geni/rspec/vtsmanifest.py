# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import os

from lxml import etree as ET

import geni.namespaces as GNS
from .pgmanifest import ManifestSvcLogin

XPNS = {'g' : GNS.REQUEST.name,
        'v' : "http://geni.bssoftworks.com/rspec/ext/vts/manifest/1",
        's' : "http://geni.bssoftworks.com/rspec/ext/sdn/manifest/1"}

class UnhandledPortTypeError(Exception):
  def __init__ (self, typ):
    super(UnhandledPortTypeError, self).__init__()
    self.typ = typ
  def __str__ (self):
    return "Port type '%s' isn't supported by port builder.  Perhaps you should contribute some code?" % (self.typ)


class GenericPort(object):
  def __init__ (self, typ):
    self.client_id = None
    self.type = typ

  @classmethod
  def _fromdom (cls, elem):
    p = GenericPort(elem.get("type"))
    p.client_id = elem.get("client_id")
    return p

  @property
  def name (self):
    # Assumes that the client_id is in the format "dp_name:port_name"
    if self.client_id.count(":") == 1:
      return self.client_id[self.client_id.index(":")+1:]
    return None
    ### TODO: Raise an exception here

  @property
  def dpname (self):
    if self.client_id.count(":") == 1:
      return self.client_id.split(":")[0]
    return None
    ### TODO: Raise an exception here


class InternalPort(GenericPort):
  class NoMACAddressError(Exception):
    def __init__ (self, cid):
      super(InternalPort.NoMACAddressError, self).__init__()
      self._cid = cid
    def __str__ (self):
      return "Port with client_id %s does not have MAC address." % (self._cid)

  def __init__ (self):
    super(InternalPort, self).__init__("internal")
    self.remote_client_id = None
    self._macaddress = None

  @property
  def macaddress (self):
    if not self._macaddress:
      raise InternalPort.NoMACAddressError(self.client_id)
    else:
      return self._macaddress

  @macaddress.setter
  def macaddress (self, val):
    self._macaddress = val

  @classmethod
  def _fromdom (cls, elem):
    p = InternalPort()
    p.client_id = elem.get("client_id")
    p.remote_client_id = elem.get("remote-clientid")
    p.macaddress = elem.get("mac-address")

    return p

  @property
  def remote_dpname (self):
    if self.remote_client_id.count(":") == 1:
      return self.remote_client_id.split(":")[0]
    return None
    ### TODO: Raise an exception here


class GREPort(GenericPort):
  def __init__ (self):
    super(GREPort, self).__init__("gre")
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


class PGLocalPort(GenericPort):
  def __init__ (self):
    super(PGLocalPort, self).__init__("pg-local")
    self.shared_vlan = None

  @classmethod
  def _fromdom (cls, elem):
    p = PGLocalPort()
    p.client_id = elem.get("client_id")
    p.shared_vlan = elem.get("shared-lan")
    return p

class ManifestContainer(object):
  def __init__ (self):
    self.name = None
    self.client_id = None
    self.image = None
    self.sliver_id = None
    self.logins = []
    self.ports = []

  @classmethod
  def _fromdom (cls, elem):
    c = ManifestContainer()
    c.name = elem.get("client_id")
    c.image = elem.get("image")
    c.sliver_id = elem.get("sliver_id")

    logins = elem.xpath('g:services/g:login', namespaces = XPNS)
    for lelem in logins:
      l = ManifestSvcLogin._fromdom(lelem)
      c.logins.append(l)

    ports = elem.xpath('v:port', namespaces = XPNS)
    for cport in ports:
      p = Manifest._buildPort(cport)
      c.ports.append(p)

    return c

class ManifestFunction(object):
  def __init__ (self, client_id):
    self.client_id = client_id

  @classmethod
  def _fromdom (cls, elem):
    typ = elem.get("type")
    if typ == "sslvpn":
      f = SSLVPNFunction._fromdom(elem)
      return f

class SSLVPNFunction(ManifestFunction):
  def __init__ (self, client_id):
    super(SSLVPNFunction, self).__init__(client_id)
    self.tp_port = None
    self.local_ip = None
    self.key = None

  @staticmethod
  def _fromdom (elem):
    return

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
    elems = self._root.xpath("v:datapath/v:port[@shared-lan]", namespaces = XPNS)
    for elem in elems:
      yield elem.get("shared-lan")

  local_circuits = pg_circuits

  @property
  def ports (self):
    elems = self._root.xpath("v:datapath/v:port", namespaces = XPNS)
    for elem in elems:
      yield Manifest._buildPort(elem)

  @property
  def containers (self):
    elems = self._root.xpath("v:container", namespaces = XPNS)
    for elem in elems:
      yield ManifestContainer._fromdom(elem)

  @property
  def functions (self):
    elems = self._root.xpath("v:functions/v:function", namespaces = XPNS)
    for elem in elems:
      yield ManifestFunction._fromdom(elem)

  def findPort (self, client_id):
    pelems = self._root.xpath("v:datapath/v:port[@client_id='%s']" % (client_id), namespaces = XPNS)
    if pelems:
      return Manifest._buildPort(pelems[0])

  @staticmethod
  def _buildPort (elem):
    t = elem.get("type")
    if t == "gre":
      return GREPort._fromdom(elem)
    elif t == "pg-local":
      return PGLocalPort._fromdom(elem)
    elif t == "vf-port":
      return GenericPort._fromdom(elem)
    elif t == "internal":
      return InternalPort._fromdom(elem)
    raise UnhandledPortTypeError(t)

  def write (self, path):
    """
.. deprecated:: 0.4
    Use :py:meth:`geni.rspec.vtsmanifest.Manifest.writeXML` instead."""

    import geni.warnings as GW
    import warnings
    warnings.warn("The Manifest.write() method is deprecated, please use Manifest.writeXML() instead",
                  GW.GENILibDeprecationWarning, 2)
    self.writeXML(path)

  def writeXML (self, path):
    f = open(path, "w+")
    f.write(ET.tostring(self.root, pretty_print=True))
    f.close()

