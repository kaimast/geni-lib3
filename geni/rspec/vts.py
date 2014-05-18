# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import geni.rspec
import geni.namespaces as GNS
from geni.rspec.pg import Resource

from lxml import etree as ET

class Namespaces(object):
  VTS = GNS.Namespace("vts", "http://geni.bssoftworks.com/rspec/ext/vts/request/1")
  SDN = GNS.Namespace("sdn", "http://geni.bssoftworks.com/rspec/ext/sdn/request/1")


###################
# Datapath Images #
###################

class DatapathImage(object):
  def __init__ (self, name):
    self.name = name
    self._features = []

  def _write (self, element):
    i = ET.SubElement(element, "{%s}image" % (Namespaces.VTS.name))
    i.attrib["name"] = self.name
    for feature in self._features:
      feature._write(i)
    return i

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


class OVSOpenFlowImage(OVSImage):
  def __init__ (self, controller):
    super(OVSOpenFlowImage, self).__init__("bss:ovs-201-of")
    self.controller = controller

  def _write (self, element):
    i = super(OVSOpenFlowImage, self)._write(element)
    c = ET.SubElement(i, "{%s}controller" % (Namespaces.SDN.name))
    c.attrib["url"] = self.controller
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


##################
# Graph Elements #
##################

class Datapath(Resource):
  def __init__ (self, image, name):
    super(Datapath, self).__init__()
    self.image = image
    self.ports = []
    self.name = name

  def attachPort (self, port):
    port.clientid = "%s:%d" % (self.name, len(self.ports))
    self.ports.append(port)

  def _write (self, element):
    d = ET.SubElement(element, "{%s}datapath" % (Namespaces.VTS.name))
    d.attrib["client_id"] = self.name
    self.image._write(d)
    for port in self.ports:
      port._write(d)
    return d


class Port(object):
  def __init__ (self):
    self.clientid = None

  def _write (self, element):
    p = ET.SubElement(element, "{%s}port" % (Namespaces.VTS.name))
    return p


class PGCircuit(Port):
  def __init__ (self):
    super(PGCircuit, self).__init__()

  def _write (self, element):
    p = super(PGCircuit, self)._write(element)
    p.attrib["type"] = "pg-local"
    return p


class InternalCircuit(Port):
  def __init__ (self, target):
    super(InternalCircuit, self).__init__()
    self.target = target

  def _write (self, element):
    p = super(InternalCircuit, self)._write(element)
    p.attrib["type"] = "internal"
    t = ET.SubElement(p, "{%s}target" % (Namespaces.VTS.name))
    t.attrib["remote-clientid"] = self.target
    return p

 
class SSLVPNCircuit(Port):
  def __init__ (self):
    super(SSLVPNCircuit, self).__init__()

  def _write (self, element):
    p = super(SSLVPNCircuit, self)._write(element)
    p.attrib["type"] = "sslvpn"
    return p


class Request(geni.rspec.RSpec):
  def __init__ (self):
    super(Request, self).__init__("request")
    self.resources = []

    self.addNamespace(GNS.REQUEST, None)
    self.addNamespace(Namespaces.VTS)
    self.addNamespace(Namespaces.SDN)

  def addResource (self, rsrc):
    for ns in rsrc.namespaces:
      self.addNamespace(ns)
    self.resources.append(rsrc)

  def write (self, path):
    f = open(path, "w+")

    rspec = self.getDOM()

    for resource in self.resources:
      resource._write(rspec)

    f.write(ET.tostring(rspec, pretty_print=True))
    f.close()
