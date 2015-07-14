# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from .pg import Node

class OFController(object):
  """OpenFlow controller specification to be used on a PG VLAN.
  
Add to link objects using the Link.addChild() method.

.. note::
  This will have no effect if a trivial link is created by the aggregate.
  You need to make sure that a VLAN will be provisioned (typically by making sure
  that at least two interfaces on the link are on different physical hosts)."""

  def __init__ (self, host, port=6633):
    self.host = host
    self.port = port

  def _write (self, element):
    eof = ET.SubElement(element, "{%s}openflow_controller" % (PGNS.EMULAB))
    eof.attrib["url"] = "tcp:%s:%d" % (self.host, self.port)
    return eof


class XenVM(Node):
  def __init__ (self, name, component_id = None, exclusive = False):
    super(XenVM, self).__init__(name, "emulab-xen", component_id = component_id, exclusive = exclusive)
    self.cores = 1
    self.ram = 256
    self.disk = 8

  def _write (self, root):
    nd = super(XenVM, self)._write(root)
    st = nd.find("{%s}sliver_type" % (GNS.REQUEST.name))
    xen = ET.SubElement(st, "{%s}xen" % (PGNS.EMULAB.name))
    xen.attrib["cores"] = str(self.cores)
    xen.attrib["ram"] = str(self.ram)
    xen.attrib["disk"] = str(self.disk)
    return nd
