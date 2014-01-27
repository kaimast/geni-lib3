# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import geni.rspec
import geni.namespaces as GNS

from lxml import etree as ET
import itertools
import uuid


class Resource(object):
  def __init__ (self):
    self.namespaces = []


class NodeType(object):
  XEN = "emulab-xen"
  RAW = "raw"
  VM = "emulab-xen"


class Command(object):
  def __init__ (self, cmd, data):
    self.cmd = cmd
    self.data = data
  
  def resolve (self):
    return self.cmd % self.data


class Service(object):
  def __init__ (self):
    pass


class Install(Service):
  def __init__ (self, url, path):
    super(Install, self).__init__()
    self.url = url
    self.path = path

  def _write (self, element):
    ins = ET.SubElement(element, "{%s}install" % (GNS.REQUEST.name))
    ins.attrib["url"] = self.url
    ins.attrib["install_path"] = self.path


class Execute(Service):
  def __init__ (self, shell, command):
    super(Execute, self).__init__()
    self.shell = shell
    self.command = command

  def _write (self, element):
    exc = ET.SubElement(element, "{%s}execute" % (GNS.REQUEST.name))
    exc.attrib["shell"] = self.shell
    if isinstance(self.command, Command):
      exc.attrib["command"] = self.command.resolve()
    else:
      exc.attrib["command"] = self.command


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
    self.component_id = None
    self.bandwidth = None

  @property
  def name (self):
    return self.client_id

  def addAddress (self, address):
    if isinstance(address, Address):
      self.addresses.append(address)
    else:
      raise Interface.InvalidAddressTypeError(address)

  def _write (self, element):
    intf = ET.SubElement(element, "{%s}interface" % (GNS.REQUEST.name))
    intf.attrib["client_id"] = self.client_id
    if self.component_id:
      intf.attrib["component_id"] = self.component_id
    for addr in self.addresses:
      addr._write(intf)


class Link(Resource):
  LNKID = 0
  DEFAULT_BW = 100000

  def __init__ (self, name = None, ltype = ""):
    super(Link, self).__init__()
    if name is None:
      self.client_id = Link.newLinkID()
    else:
      self.client_id = name
    self.interfaces = []
    self.type = ltype
    self.shared_vlan = None
    self._mac_learning = True

    # If you try to set bandwidth higher than a gigabit, PG probably won't like you
    self.bandwidth = Link.DEFAULT_BW

  @classmethod
  def newLinkID (cls):
    Link.LNKID += 1
    return "link-%d" % (Link.LNKID)

  def addInterface (self, intf):
    self.interfaces.append(intf)

  def connectSharedVlan (self, name):
    self.namespaces.append(GNS.SVLAN)
    self.shared_vlan = name

  def disableMACLearning (self):
    self.namespaces.append(Namespaces.VTOP)
    self._mac_learning = False

  def _write (self, root):
    lnk = ET.SubElement(root, "{%s}link" % (GNS.REQUEST.name))
    lnk.attrib["client_id"] = self.client_id
    for intf in self.interfaces:
      ir = ET.SubElement(lnk, "{%s}interface_ref" % (GNS.REQUEST.name))
      ir.attrib["client_id"] = intf.client_id
    if self.type != "":
      lt = ET.SubElement(lnk, "{%s}link_type" % (GNS.REQUEST.name))
      lt.attrib["name"] = self.type
    if self.shared_vlan:
      sv = ET.SubElement(lnk, "{%s}link_shared_vlan" % (GNS.SVLAN.name))
      sv.attrib["name"] = self.shared_vlan

    if self.bandwidth != Link.DEFAULT_BW:
      for (src,dst) in itertools.permutations(self.interfaces):
        bw = ET.SubElement(lnk, "{%s}property" % (GNS.REQUEST.name))
        bw.attrib["capacity"] = "%d" % (self.bandwidth)
        bw.attrib["source_id"] = src.client_id
        bw.attrib["dest_id"] = dst.client_id

    if not self._mac_learning:
      lrnelem = ET.SubElement(lnk, "{%s}link_attribute" % (Namespaces.VTOP.name))
      lrnelem.attrib["key"] = "nomac_learning"
      lrnelem.attrib["value"] = "yep"

    for intf in self.interfaces:
      if intf.bandwidth:
        for other in self.interfaces:
          if intf is not other:
            prop = ET.SubElement(lnk, "{%s}property" % (GNS.REQUEST.name))
            prop.attrib["source_id"] = other.name
            prop.attrib["dest_id"] = intf.name
            prop.attrib["capacity"] = str(intf.bandwidth)


class LAN(Link):
  def __init__ (self, name = None):
    super(LAN, self).__init__(name, "lan")


class Node(Resource):
  def __init__ (self, name, ntype, component_id = None, exclusive = False):
    super(Node, self).__init__()
    self.client_id = name
    self.exclusive = exclusive
    self.disk_image = None
    self.type = ntype
    self.interfaces = []
    self.services = []
    self.routable_control_ip = False
    self.component_id = component_id

  @property
  def name (self):
    return self.client_id

  def _write (self, root):
    nd = ET.SubElement(root, "{%s}node" % (GNS.REQUEST.name))
    nd.attrib["client_id"] = self.client_id
    nd.attrib["exclusive"] = str(self.exclusive).lower()
    if self.component_id:
      nd.attrib["component_id"] = self.component_id
    
    st = ET.SubElement(nd, "{%s}sliver_type" % (GNS.REQUEST.name))
    st.attrib["name"] = self.type

    if self.disk_image:
      di = ET.SubElement(st, "{%s}disk_image" % (GNS.REQUEST.name))
      di.attrib["name"] = self.disk_image

    if self.interfaces:
      for intf in self.interfaces:
        intf._write(nd)

    if self.services:
      svc = ET.SubElement(nd, "{%s}services" % (GNS.REQUEST.name))
      for service in self.services:
        service._write(svce)

    if self.routable_control_ip:
      rc = ET.SubElement(nd, "{%s}routable_control_ip")

    return nd

  def addInterface (self, name):
    intf = Interface("%s:%s" % (self.client_id, name), self)
    self.interfaces.append(intf)
    return intf

  def addService (self, svc):
    self.services.append(svc)


class RawPC(Node):
  def __init__ (self, name, component_id = None):
    super(RawPC, self).__init__(name, NodeType.RAW, component_id = component_id, exclusive = True)


class XenVM(Node):
  def __init__ (self, name, component_id = None, exclusive = False):
    super(XenVM, self).__init__(name, NodeType.XEN, component_id = component_id, exclusive = exclusive)


class VZContainer(Node):
  def __init__ (self, name, exclusive = False):
    super(VZContainer, self).__init__(name, "emulab-openvz", exclusive)

VM = XenVM


class Namespaces(object):
  CLIENT = GNS.Namespace("client", "http://www.protogeni.net/resources/rspec/ext/client/1")
  RS = GNS.Namespace("rs", "http://www.protogeni.net/resources/rspec/ext/emulab/1")
  EMULAB = GNS.Namespace("emulab", "http://www.protogeni.net/resources/rspec/ext/emulab/1")
  VTOP  = GNS.Namespace("vtop", "http://www.protogeni.net/resources/rspec/ext/emulab/1", "vtop_extension.xsd")


class XMLContext(object):
  def __init__ (self, rspec, root, cur_elem = None):
    self.rspec = rspec
    self.root = root
    self.curelem = cur_elem


class PGContext(XMLContext):
  pass


class Request(geni.rspec.RSpec):
  def __init__ (self):
    super(Request, self).__init__("request")
    self.resources = []

    self.addNamespace(GNS.REQUEST, None)
    self.addNamespace(Namespaces.CLIENT)

  def addResource (self, rsrc):
    for ns in rsrc.namespaces:
      self.addNamespace(ns)
    self.resources.append(rsrc)

  def write (self, path):
    f = open(path, "w+")

    rspec = self.getDOM()
#ctx = Context(self, rspec)

    for resource in self.resources:
      resource._write(rspec)

    f.write(ET.tostring(rspec, pretty_print=True))
    f.close()
