# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import geni.rspec
import geni.namespaces as GNS
import geni.urn

from lxml import etree as ET
import itertools
import uuid
import sys
import functools


class Resource(object):
  def __init__ (self):
    self.namespaces = []

  def addNamespace (self, ns):
    self.namespaces.append(ns)


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
      if isinstance(self.component_id, geni.urn.Base):
        intf.attrib["component_id"] = str(self.component_id)
      else:
        intf.attrib["component_id"] = self.component_id
    for addr in self.addresses:
      addr._write(intf)


class Link(Resource):
  LNKID = 0
  DEFAULT_BW = -1

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
    self._vlan_tagging = False
    self._link_multiplexing = False
    self._best_effort = False
    self._ext_children = []

    # If you try to set bandwidth higher than a gigabit, PG probably won't like you
    self.bandwidth = Link.DEFAULT_BW

  @classmethod
  def newLinkID (cls):
    Link.LNKID += 1
    return "link-%d" % (Link.LNKID)

  def addChild (self, obj):
    self._ext_children.append(obj)

  def addInterface (self, intf):
    self.interfaces.append(intf)

  def connectSharedVlan (self, name):
    self.namespaces.append(GNS.SVLAN)
    self.shared_vlan = name

  def disableMACLearning (self):
    self.namespaces.append(Namespaces.VTOP)
    self._mac_learning = False

  def enableVlanTagging (self):
    import geni.warnings as GW
    import warnings
    warnings.warn("Link.enableVlanTagging() is deprecated, please use the Link.vlan_tagging attribute instead.")
    self.vlan_tagging = True

  @property
  def vlan_tagging (self):
    return self._vlan_tagging

  @vlan_tagging.setter
  def vlan_tagging (self, val):
    self.namespaces.append(Namespaces.EMULAB)
    self._vlan_tagging = val 

  @property
  def best_effort (self):
    return self._best_effort

  @best_effort.setter
  def best_effort (self, val):
    self.namespaces.append(Namespaces.EMULAB)
    self._best_effort = val

  @property
  def link_multiplexing (self):
    return self._link_multiplexing

  @link_multiplexing.setter
  def link_multiplexing (self, val):
    self.namespaces.append(Namespaces.EMULAB)
    self._link_multiplexing = val

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

    if not self._mac_learning:
      lrnelem = ET.SubElement(lnk, "{%s}link_attribute" % (Namespaces.VTOP.name))
      lrnelem.attrib["key"] = "nomac_learning"
      lrnelem.attrib["value"] = "yep"

    if self._vlan_tagging:
      tagging = ET.SubElement(lnk, "{%s}vlan_tagging" % (Namespaces.EMULAB.name))
      tagging.attrib["enabled"] = "true"

    if self._best_effort:
      tagging = ET.SubElement(lnk, "{%s}best_effort" % (Namespaces.EMULAB.name))
      tagging.attrib["enabled"] = "true"

    if self._link_multiplexing:
      tagging = ET.SubElement(lnk, "{%s}link_multiplexing" % (Namespaces.EMULAB.name))
      tagging.attrib["enabled"] = "true"

    ################
    # These are...sortof duplicate (but not quite).  We should sort that out.
    if self.bandwidth != Link.DEFAULT_BW:
      if len(self.interfaces) >= 2:
        for (src,dst) in itertools.permutations(self.interfaces):
          bw = ET.SubElement(lnk, "{%s}property" % (GNS.REQUEST.name))
          bw.attrib["capacity"] = "%d" % (self.bandwidth)
          bw.attrib["source_id"] = src.client_id
          bw.attrib["dest_id"] = dst.client_id

    for intf in self.interfaces:
      if intf.bandwidth:
        for other in self.interfaces:
          if intf is not other:
            prop = ET.SubElement(lnk, "{%s}property" % (GNS.REQUEST.name))
            prop.attrib["source_id"] = other.name
            prop.attrib["dest_id"] = intf.name
            prop.attrib["capacity"] = str(intf.bandwidth)
    ################

    for obj in self._ext_children:
      obj._write(lnk)

    return lnk


class LAN(Link):
  def __init__ (self, name = None):
    super(LAN, self).__init__(name, "lan")

class L3GRE(Link):
  def __init__ (self, name = None):
    super(L3GRE, self).__init__(name, "gre-tunnel")

class L2GRE(Link):
  def __init__ (self, name = None):
    super(L2GRE, self).__init__(name, "egre-tunnel")

class StitchedLink(Link):
  class UnknownComponentManagerError(Exception):
    def __init__ (self, cid):
      self._cid = cid
    def __str__ (self):
      return "Interface with client_id %s is not attached to a bound node." % (self._cid)

  class TooManyInterfacesError(Exception):
    def __str__ (self):
      return "Stitched Links may not be connected to more than two interfaces"

  def __init__ (self, name = None):
    super(StitchedLink, self).__init__(name, "")
    self.bandwidth = 20000

  def _write (self, root):
    if len(self.interfaces) > 2:
      raise StitchedLink.TooManyInterfacesError()

    lnk = super(StitchedLink, self)._write(root)
    for intf in self.interfaces:
      if intf.node.component_manager_id is None:
        raise StitchedLink.UnknownComponentManagerError(intf.client_id)
      cm = ET.SubElement(lnk, "{%s}component_manager" % (GNS.REQUEST.name))
      cm.attrib["name"] = intf.node.component_manager_id
    return lnk


class Node(Resource):
  EXTENSIONS = []

  def __init__ (self, name, ntype, component_id = None, exclusive = None):
    super(Node, self).__init__()
    self.client_id = name
    self.exclusive = exclusive
    self.disk_image = None
    self.type = ntype
    self.hardware_type = None
    self.interfaces = []
    self.services = []
    self.routable_control_ip = False
    self.component_id = component_id
    self.component_manager_id = None
    self._ext_children = []
    for name,ext in Node.EXTENSIONS:
      self._wrapext(name,ext)

  class DuplicateInterfaceName(Exception):
    def __str__ (self):
      return "Duplicate interface names"

  def _wrapext (self, name, klass):
    @functools.wraps(klass.__init__)
    def wrap(*args, **kw):
      instance = klass(*args, **kw)
      self._ext_children.append(instance)
      return instance
    setattr(self, name, wrap)

  @property
  def name (self):
    return self.client_id

  def _write (self, root):
    nd = ET.SubElement(root, "{%s}node" % (GNS.REQUEST.name))
    nd.attrib["client_id"] = self.client_id
    if self.exclusive is not None:  # Don't write this for EG
      nd.attrib["exclusive"] = str(self.exclusive).lower()
    if self.component_id:
      if isinstance(self.component_id, geni.urn.Base):
        nd.attrib["component_id"] = str(self.component_id)
      else:
        nd.attrib["component_id"] = self.component_id
    if self.component_manager_id:
      if isinstance(self.component_manager_id, geni.urn.Base):
        nd.attrib["component_manager_id"] = str(self.component_manager_id)
      else:
        nd.attrib["component_manager_id"] = self.component_manager_id
    
    st = ET.SubElement(nd, "{%s}sliver_type" % (GNS.REQUEST.name))
    st.attrib["name"] = self.type

    if self.disk_image:
      # TODO: Force disk images to be objects, and stop supporting old style strings
      if isinstance(self.disk_image, (str, unicode)):
        di = ET.SubElement(st, "{%s}disk_image" % (GNS.REQUEST.name))
        di.attrib["name"] = self.disk_image
      elif isinstance(self.disk_image, geni.urn.Base):
        di = ET.SubElement(st, "{%s}disk_image" % (GNS.REQUEST.name))
        di.attrib["name"] = str(self.disk_image)
      else:
        self.disk_image._write(st)

    if self.hardware_type:
        hwt = ET.SubElement(nd, "{%s}hardware_type" % (GNS.REQUEST.name))
        hwt.attrib["name"] = self.hardware_type

    if self.interfaces:
      for intf in self.interfaces:
        intf._write(nd)

    if self.services:
      svc = ET.SubElement(nd, "{%s}services" % (GNS.REQUEST.name))
      for service in self.services:
        service._write(svc)

    if self.routable_control_ip:
      rc = ET.SubElement(nd, "{%s}routable_control_ip" % (Namespaces.EMULAB.name))

    for obj in self._ext_children:
      obj._write(nd)

    return nd

  def addInterface (self, name = None):
    existingNames = map(lambda x: getattr(x,'name'), self.interfaces)
    if name is not None:
      intfName = "%s:%s" % (self.client_id, name)
    else:
      for i in range(0, 100):
        intfName = "%s:if%i" % (self.client_id, i)
        if intfName not in existingNames:
          break

    if intfName in existingNames:
      raise Node.DuplicateInterfaceName()

    intf = Interface(intfName, self)
    self.interfaces.append(intf)
    return intf

  def addService (self, svc):
    self.services.append(svc)


class RawPC(Node):
  def __init__ (self, name, component_id = None):
    super(RawPC, self).__init__(name, NodeType.RAW, component_id = component_id, exclusive = True)



class VZContainer(Node):
  def __init__ (self, name, exclusive = False):
    super(VZContainer, self).__init__(name, "emulab-openvz", exclusive)



class Namespaces(object):
  CLIENT = GNS.Namespace("client", "http://www.protogeni.net/resources/rspec/ext/client/1")
  RS = GNS.Namespace("rs", "http://www.protogeni.net/resources/rspec/ext/emulab/1")
  EMULAB = GNS.Namespace("emulab", "http://www.protogeni.net/resources/rspec/ext/emulab/1")
  VTOP  = GNS.Namespace("vtop", "http://www.protogeni.net/resources/rspec/ext/emulab/1", "vtop_extension.xsd")
  TOUR =  GNS.Namespace("tour", "http://www.protogeni.net/resources/rspec/ext/apt-tour/1")
  JACKS = GNS.Namespace("jacks", "http://www.protogeni.net/resources/rspec/ext/jacks/1")


class Request(geni.rspec.RSpec):
  def __init__ (self):
    super(Request, self).__init__("request")
    self.resources = []
    self.tour = None

    self.addNamespace(GNS.REQUEST, None)
    self.addNamespace(Namespaces.CLIENT)

  def addResource (self, rsrc):
    for ns in rsrc.namespaces:
      self.addNamespace(ns)
    self.resources.append(rsrc)

  def addTour (self, tour):
    self.addNamespace(Namespaces.EMULAB)
    self.addNamespace(Namespaces.JACKS)
    self.tour = tour

  def writeXML (self, path):
    """Write the current request contents as an XML file that represents an rspec
    in the GENIv3 format."""

    if path is None:
      f = sys.stdout
    else:
      f = open(path, "w+")

    rspec = self.getDOM()

    if self.tour:
      self.tour._write(rspec)

    for resource in self.resources:
      resource._write(rspec)

    f.write(ET.tostring(rspec, pretty_print=True))
    
    if path is not None:
      f.close()

  def toXMLString (self, pretty_print = False):
    """Return the current request contents as an XML string that represents an rspec
    in the GENIv3 format."""

    rspec = self.getDOM()

    if self.tour:
      self.tour._write(rspec)

    for resource in self.resources:
      resource._write(rspec)

    buf = ET.tostring(rspec, pretty_print = pretty_print)
    return buf

  def write (self, path):
    """
.. deprecated:: 0.4
    Use :py:meth:`geni.rspec.pg.Request.writeXML` instead."""

    import geni.warnings as GW
    import warnings
    warnings.warn("The Request.write() method is deprecated, please use Request.writeXML() instead",
                  GW.GENILibDeprecationWarning, 2)
    self.writeXML(path)

#### DEPRECATED #####
class XenVM(Node):
  """
.. deprecated:: 0.4
   Use :py:class:`geni.rspec.igext.XenVM` instead."""
  def __init__ (self, name, component_id = None, exclusive = False):
    import geni.warnings as GW
    import warnings
    warnings.warn("geni.rspec.pg.XenVM is deprecated, please use geni.rspec.igext.XenVM instead", 
                  GW.GENILibDeprecationWarning)
    super(XenVM, self).__init__(name, NodeType.XEN, component_id = component_id, exclusive = exclusive)
    self.cores = 1
    self.ram = 256
    self.disk = 8

  def _write (self, root):
    nd = super(XenVM, self)._write(root)
    st = nd.find("{%s}sliver_type" % (GNS.REQUEST.name))
    xen = ET.SubElement(st, "{%s}xen" % (Namespaces.EMULAB.name))
    xen.attrib["cores"] = str(self.cores)
    xen.attrib["ram"] = str(self.ram)
    xen.attrib["disk"] = str(self.disk)
    return nd

VM = XenVM

