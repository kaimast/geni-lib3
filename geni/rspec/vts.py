# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import functools
import decimal

import ipaddress
from lxml import etree as ET

import geni.rspec
import geni.namespaces as GNS
from geni.rspec.pg import Resource


class Namespaces(object):
  VTS = GNS.Namespace("vts", "http://geni.bssoftworks.com/rspec/ext/vts/request/1")
  SDN = GNS.Namespace("sdn", "http://geni.bssoftworks.com/rspec/ext/sdn/request/1")

################################################
# Base Request - Must be at top for EXTENSIONS #
################################################

class Request(geni.rspec.RSpec):
  EXTENSIONS = []

  def __init__ (self):
    super(Request, self).__init__("request")
    self._resources = []

    self.addNamespace(GNS.REQUEST, None)
    self.addNamespace(Namespaces.VTS)
    self.addNamespace(Namespaces.SDN)

    self._ext_children = []
    for name,ext in Request.EXTENSIONS:
      self._wrapext(name,ext)

  def _wrapext (self, name, klass):
    @functools.wraps(klass.__init__)
    def wrap(*args, **kw):
      instance = klass(*args, **kw)
      self._ext_children.append(instance)
      return instance
    setattr(self, name, wrap)

  def addResource (self, rsrc):
    for ns in rsrc.namespaces:
      self.addNamespace(ns)
    self._resources.append(rsrc)

  def writeXML (self, path):
    f = open(path, "w+")
    f.write(self.toXMLString(True))
    f.close()

  def toXMLString (self, pretty_print = False):
    rspec = self.getDOM()

    for resource in self._resources:
      resource._write(rspec)

    for obj in self._ext_children:
      obj._write(rspec)

    buf = ET.tostring(rspec, pretty_print = pretty_print)
    return buf

  @property
  def resources(self):
      return self._resources + self._ext_children

###################
# Utility Objects #
###################

class DelayInfo(object):
  def __init__ (self, time = None, jitter = None, correlation = None, distribution = None):
    self.time = time
    self.jitter = jitter
    self.correlation = correlation
    self.distribution = distribution

  def __json__ (self):
    d = {"type" : "egress-delay"}
    if self.time: d["time"] = self.time
    if self.jitter: d["jitter"] = self.jitter
    if self.correlation: d["correlation"] = self.correlation
    if self.distribution: d["distribution"] = self.distribution
    return d

  def _write (self, element):
    d = ET.SubElement(element, "{%s}egress-delay" % (Namespaces.VTS.name))
    if self.time: d.attrib["time"] = str(self.time)
    if self.jitter: d.attrib["jitter"] = str(self.jitter)
    if self.correlation: d.attrib["correlation"] = str(self.correlation)
    if self.distribution: d.attrib["distribution"] = self.distribution
    return d


class LossInfo(object):
  def __init__ (self, percent):
    self._percent = None
    self.percent = percent

  @property
  def percent (self):
    return self._percent

  @percent.setter
  def percent (self, val):
    self._percent = decimal.Decimal(val)

  def __json__ (self):
    return {"type" : "egress-loss", "percent" : "%s" % (self.percent)}

  def _write (self, element):
    d = ET.SubElement(element, "{%s}egress-loss" % (Namespaces.VTS))
    d.attrib["percent"] = "%s" % (self.percent)
    return d


###################
# Datapath Images #
###################

class Image(object):
  def __init__ (self, name):
    self.name = name
    self._features = []
    self._image_attrs = []

  def setImageAttribute (self, name, val):
    self._image_attrs.append((name, val))

  def _write (self, element):
    i = ET.SubElement(element, "{%s}image" % (Namespaces.VTS.name))
    i.attrib["name"] = self.name
    for feature in self._features:
      feature._write(i)
    for (name,val) in self._image_attrs:
      ae = ET.SubElement(i, "{%s}image-attribute" % (Namespaces.VTS))
      ae.attrib["name"] = name
      ae.attrib["value"] = str(val)
    return i

class SimpleDHCPImage(Image):
  def __init__ (self, subnet = None):
    super(SimpleDHCPImage, self).__init__("uh.simple-dhcpd")
    self.subnet = subnet

  def _write (self, element):
    e = super(SimpleDHCPImage, self)._write(element)
    if self.subnet:
      subnet = ET.SubElement(e, "{%s}image-attribute" % (Namespaces.VTS))
      subnet.attrib["name"] = "subnet"
      subnet.attrib["value"] = str(self.subnet)
    return e


class DatapathImage(Image):
  pass

class OVSImage(DatapathImage):
  def __init__ (self, name):
    super(OVSImage, self).__init__(name)

  @property
  def sflow (self):
    return None

  @sflow.setter
  def sflow (self, val):
    if isinstance(val, SFlow):
      self._features.append(val)
    # TODO: Throw exception

  @property
  def netflow (self):
    return None

  @netflow.setter
  def netflow (self, val):
    if isinstance(val, NetFlow):
      self._features.append(val)
    # TODO: Throw exception

  def setMirror (self, port):
    self._features.append(MirrorPort(port))


class OVSOpenFlowImage(OVSImage):
  def __init__ (self, controller, ofver = "1.0", dpid = None):
    super(OVSOpenFlowImage, self).__init__("bss:ovs-201-of")
    self.dpid = dpid
    self.controller = controller
    self.ofver = ofver

  def _write (self, element):
    i = super(OVSOpenFlowImage, self)._write(element)
    c = ET.SubElement(i, "{%s}controller" % (Namespaces.SDN.name))
    c.attrib["url"] = self.controller

    v = ET.SubElement(i, "{%s}openflow-version" % (Namespaces.VTS.name))
    v.attrib["value"] = self.ofver

    if self.dpid:
      d = ET.SubElement(i, "{%s}openflow-dpid" % (Namespaces.VTS.name))
      d.attrib["value"] = str(self.dpid)

    return i

class OVSL2Image(OVSImage):
  def __init__ (self):
    super(OVSL2Image, self).__init__("bss:ovs-201")

##################
# Image Features #
##################

class SFlow(object):
  def __init__ (self, collector_ip):
    self.collector_ip = collector_ip
    self.collector_port = 6343
    self.header_bytes = 128
    self.sampling_n = 64
    self.polling_secs = 5

  def _write (self, element):
    s = ET.SubElement(element, "{%s}sflow" % (Namespaces.VTS.name))
    s.attrib["collector"] = "%s:%d" % (self.collector_ip, self.collector_port)
    s.attrib["header-bytes"] = str(self.header_bytes)
    s.attrib["sampling-n"] = str(self.sampling_n)
    s.attrib["polling-secs"] = str(self.polling_secs)
    return s


class NetFlow(object):
  def __init__ (self, collector_ip):
    self.collector_ip = collector_ip
    self.collector_port = 6343
    self.timeout = 20

  def _write (self, element):
    s = ET.SubElement(element, "{%s}netflow" % (Namespaces.VTS))
    s.attrib["collector"] = "%s:%d" % (self.collector_ip, self.collector_port)
    s.attrib["timeout"] = str(self.timeout)
    return s

class MirrorPort(object):
  def __init__ (self, port):
    self.target = port.client_id

  def _write (self, element):
    s = ET.SubElement(element, "{%s}mirror" % (Namespaces.VTS))
    s.attrib["target"] = self.target
    return s

##################
# Graph Elements #
##################

class SSLVPNFunction(Resource):
  def __init__ (self, client_id):
    super(SSLVPNFunction, self).__init__()
    self.client_id = client_id
    self.protocol = None

  def _write (self, element):
    d = ET.SubElement(element, "{%s}function" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.client_id
    d.attrib["type"] = "sslvpn"
    return d

Request.EXTENSIONS.append(("SSLVPNFunction", SSLVPNFunction))

class Datapath(Resource):
  def __init__ (self, image, client_id):
    super(Datapath, self).__init__()
    self.image = image
    self.ports = []
    self.client_id = client_id

  @property
  def name (self):
    return self.client_id

  @name.setter
  def name (self, val):
    self.client_id = val

  def attachPort (self, port):
    if port.client_id is None:
      if port.name is None:
        port.client_id = "%s:%d" % (self.name, len(self.ports))
      else:
        port.client_id = "%s:%s" % (self.name, port.name)
    self.ports.append(port)
    return port

  def _write (self, element):
    d = ET.SubElement(element, "{%s}datapath" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.name
    self.image._write(d)
    for port in self.ports:
      port._write(d)
    return d

Request.EXTENSIONS.append(("Datapath", Datapath))


class Container(Resource):
  EXTENSIONS = []

  def __init__ (self, image, name):
    super(Container, self).__init__()
    self.image = image
    self.ports =[]
    self.name = name
    self.routes = []

    for name,ext in Container.EXTENSIONS:
      self._wrapext(name, ext)

  def attachPort (self, port):
    if port.name is None:
      port.client_id = "%s:%d" % (self.name, len(self.ports))
    else:
      port.client_id = "%s:%s" % (self.name, port.name)
    self.ports.append(port)
    return port

  def addIPRoute (self, network, gateway):
    self.routes.append((ipaddress.IPv4Network(unicode(network)), ipaddress.IPv4Address(unicode(gateway))))

  def _write (self, element):
    d = ET.SubElement(element, "{%s}container" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.name
    self.image._write(d)
    for port in self.ports:
      port._write(d)
    for net,gw in self.routes:
      re = ET.SubElement(d, "{%s}route" % (Namespaces.VTS))
      re.attrib["network"] = str(net)
      re.attrib["gateway"] = str(gw)
    super(Container, self)._write(d)
    return d

Request.EXTENSIONS.append(("Container", Container))


class Port(object):
  def __init__ (self, name = None):
    self.client_id = None
    self.name = name

  def _write (self, element):
    p = ET.SubElement(element, "{%s}port" % (Namespaces.VTS.name))
    p.attrib["client_id"] = self.client_id
    return p


class PGCircuit(Port):
  def __init__ (self, name = None, delay_info = None):
    super(PGCircuit, self).__init__(name)
    self.delay_info = delay_info

  def _write (self, element):
    p = super(PGCircuit, self)._write(element)
    p.attrib["type"] = "pg-local"
    if self.delay_info:
      self.delay_info._write(p)
    return p

LocalCircuit = PGCircuit

class VFCircuit(Port):
  def __init__ (self, target):
    super(VFCircuit, self).__init__()
    self.target = target

  def _write (self, element):
    p = super(VFCircuit, self)._write(element)
    p.attrib["type"] = "vf-port"
    t = ET.SubElement(p, "{%s}target" % (Namespaces.VTS.name))
    t.attrib["remote-clientid"] = self.target
    return p


class InternalCircuit(Port):
  def __init__ (self, target, vlan = None, delay_info = None, loss_info = None):
    super(InternalCircuit, self).__init__()
    self.vlan = vlan
    self.target = target
    self.delay_info = delay_info
    self.loss_info = loss_info

  def _write (self, element):
    p = super(InternalCircuit, self)._write(element)
    p.attrib["type"] = "internal"
    if self.vlan:
      p.attrib["vlan-id"] = str(self.vlan)
    if self.delay_info: self.delay_info._write(p)
    if self.loss_info: self.loss_info._write(p)
    t = ET.SubElement(p, "{%s}target" % (Namespaces.VTS.name))
    t.attrib["remote-clientid"] = self.target
    return p


class ContainerPort(InternalCircuit):
  def __init__ (self, target, vlan = None, delay_info = None, loss_info = None):
    super(ContainerPort, self).__init__(target, vlan, delay_info, loss_info)
    self._v4addresses = []

  def _write (self, element):
    p = super(ContainerPort, self)._write(element)
    for addr in self._v4addresses:
      ae = ET.SubElement(p, "{%s}ipv4-address" % (Namespaces.VTS))
      ae.attrib["value"] = str(addr)
    return p

  def addIPv4Address (self, value):
    self._v4addresses.append(ipaddress.IPv4Interface(unicode(value)))


class GRECircuit(Port):
  def __init__ (self, circuit_plane, endpoint):
    super(GRECircuit, self).__init__()
    self.circuit_plane = circuit_plane
    self.endpoint = endpoint

  def _write (self, element):
    p = super(GRECircuit, self)._write(element)
    p.attrib["type"] = "gre"
    p.attrib["circuit-plane"] = self.circuit_plane
    p.attrib["endpoint"] = self.endpoint
    return p


######################
# Element Extensions #
######################

class HgMount(Resource):
  def __init__ (self, name, source, mount_path, branch = "default"):
    self.name = name
    self.source = source
    self.mount_path = mount_path
    self.branch = branch

  def _write (self, element):
    melem = ET.SubElement(element, "{%s}mount" % (Namespaces.VTS))
    melem.attrib["type"] = "hg"
    melem.attrib["name"] = self.name
    melem.attrib["path"] = self.mount_path
    melem.attrib["source"] = self.source
    melem.attrib["branch"] = self.branch
    return melem

Container.EXTENSIONS.append(("HgMount", HgMount))


#############
# Utilities #
#############

def connectInternalCircuit (dp1, dp2, delay_info = None, loss_info = None):
  dp1v = None
  dp2v = None

  if isinstance(dp1, tuple):
    dp1v = dp1[1]
    dp1 = dp1[0]

  if isinstance(dp2, tuple):
    dp2v = dp2[1]
    dp2 = dp2[0]

  if isinstance(dp1, Container):
    sp = ContainerPort(None, dp1v, delay_info, loss_info)
  elif isinstance(dp1, Datapath):
    sp = InternalCircuit(None, dp1v, delay_info, loss_info)

  if isinstance(dp2, Container):
    dp = ContainerPort(None, dp2v, delay_info, loss_info)
  elif isinstance(dp2, Datapath):
    dp = InternalCircuit(None, dp2v, delay_info, loss_info)

  dp1.attachPort(sp)
  dp2.attachPort(dp)

  sp.target = dp.client_id
  dp.target = sp.client_id

  return (sp, dp)
