# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import
import geni.rspec
import geni.namespaces as GNS

from lxml import etree as ET

class NodeType(object):
  XEN = "emulab-xen"
  RAW = "raw"
  VM = "emulab-xen"


class Address(object):
  def __init__ (self, atype):
    self.type = atype


class IPv4Address(Address):
  def __init__ (self, address, netmask):
    super(IPv4Address, self).__init__("ipv4")
    self.address = address
    self.netmask = netmask

  def _write (self, element):
    ip = ET.SubElement(element, "{%s}ip" % (GNS.REQUEST.name))
    ip.attrib["address"] = self.address
    ip.attrib["netmask"] = self.netmask
    ip.attrib["type"] = self.type


class Interface(object):
  class InvalidAddressTypeError(Exception):
    def __init__ (self, addr):
      self.addr = addr
    def __str__ (self):
      return "Type (%s) is invalid for interface addresses." % (type(self.addr))

  def __init__ (self, name, node):
    self.client_id = name
    self.node = node
    self.addresses = []

  def addAddress (self, address):
    if isinstance(address, Address):
      self.addresses.append(address)
    else:
      raise Interface.InvalidAddressTypeError(address)

  def _write (self, element):
    intf = ET.SubElement(element, "{%s}interface" % (GNS.REQUEST.name))
    intf.attrib["client_id"] = self.client_id
    for addr in self.addresses:
      addr._write(intf)


class Link(object):
  def __init__ (self, name, ltype = ""):
    self.client_id = name
    self.interfaces = []
    self.type = ltype
    self.shared_vlan = None

  def addInterface (self, intf):
    self.interfaces.append(intf)

  def connectSharedVlan (self, name):
    self.shared_vlan = name

  def _write (self, root):
    lnk = ET.SubElement(root, "{%s}link" % (GNS.REQUEST.name))
    for intf in self.interfaces:
      ir = ET.SubElement(lnk, "{%s}interface_ref" % (GNS.REQUEST.name))
      ir.attrib["client_id"] = intf.client_id
    if self.type != "":
      lt = ET.SubElement(lnk, "{%s}link_type" % (GNS.REQUEST.name))
      lt.attrib["name"] = self.type
    if self.shared_vlan:
      sv = ET.SubElement(lnk, "{%s}link_shared_vlan" % (GNS.SVLAN.name))
      sv.attrib["name"] = self.shared_vlan


class LAN(Link):
  def __init__ (self, name):
    super(LAN, self).__init__(name, "lan")


class Node(object):
  def __init__ (self, name, ntype, exclusive = False):
    self.client_id = name
    self.exclusive = exclusive
    self.disk_image = None
    self.type = ntype
    self.interfaces = []

  def _write (self, root):
    nd = ET.SubElement(root, "{%s}node" % (GNS.REQUEST.name))
    nd.attrib["client_id"] = self.client_id
    nd.attrib["exclusive"] = str(self.exclusive).lower()
    
    st = ET.SubElement(nd, "{%s}sliver_type" % (GNS.REQUEST.name))
    st.attrib["name"] = self.type

    if self.disk_image:
      di = ET.SubElement(st, "{%s}disk_image" % (GNS.REQUEST.name))
      di.attrib["name"] = self.disk_image

    if self.interfaces:
      for intf in self.interfaces:
        intf._write(nd)

  def addInterface (self, name):
    intf = Interface("%s:%s" % (self.client_id, name), self)
    self.interfaces.append(intf)
    return intf


class RawPC(Node):
  def __init__ (self, name):
    super(RawPC, self).__init__(name, NodeType.RAW, True)


class XenVM(Node):
  def __init__ (self, name, exclusive = False):
    super(XenVM, self).__init__(name, NodeType.XEN, exclusive)

VM = XenVM


class Namespaces(object):
  CLIENT = GNS.Namespace("client", "http://www.protogeni.net/resources/rspec/ext/client/1")
  RS = GNS.Namespace("rs", "http://www.protogeni.net/resources/rspec/ext/emulab/1")

class Request(geni.rspec.RSpec):
  def __init__ (self):
    super(Request, self).__init__("request")
    self.resources = []

    self.addNamespace(GNS.REQUEST, None)
    self.addNamespace(Namespaces.CLIENT)
    self.addNamespace(Namespaces.RS)

  def addResource (self, rsrc):
    self.resources.append(rsrc)

  def write (self, path):
    f = open(path, "w+")

    rspec = self.getDOM()
    for resource in self.resources:
      resource._write(rspec)

    f.write(ET.tostring(rspec, pretty_print=True))
    f.close()
