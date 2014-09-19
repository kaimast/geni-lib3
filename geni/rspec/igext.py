# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

from .pg import Namespaces as PGNS

class OFController(object):
  """OpenFlow controller specification to be used on a PG VLAN.
  
Add to link objects using the Link.addChild() method.

NOTE: This will have no effect if a trivial link is created by the aggregate.
You need to make sure that a VLAN will be provisioned (typically by making sure
that at least two interfaces on the link are on different physical hosts)."""

  def __init__ (self, host, port=6633):
    self.host = host
    self.port = port

  def _write (self, element):
    eof = ET.SubElement(element, "{%s}openflow_controller" % (PGNS.EMULAB))
    eof.attrib["url"] = "tcp:%s:%d" % (self.host, self.port)
    return eof
