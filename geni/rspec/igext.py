# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from lxml import etree as ET

from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from .pg import Node
from .pg import Resource
from . import pg
from .. import urn

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


class AddressPool(Resource):
  """A pool of public dynamic IP addresses belonging to a slice."""

  def __init__(self, name, count=1, type="any"):
    super(AddressPool, self).__init__()
    self.client_id = name
    self.count = count
    self.type = type
    self.component_manager_id = None

  @property
  def name (self):
    return self.client_id

  def _write (self, root):
    pl = ET.SubElement(root, "{%s}routable_pool" % (PGNS.EMULAB.name))
    pl.attrib["client_id"] = self.client_id
    if self.component_manager_id:
      pl.attrib["component_manager_id"] = self.component_manager_id

    pl.attrib["count"] = str(self.count)
    pl.attrib["type"] = self.type

    return pl

class Blockstore(object):
  def __init__ (self, name, mount):
    """Creates a BlockStore object with the given name (arbitrary) and mountpoint."""
    self.name = name
    self.mount = mount
    self.size = None
    self.where = "local"    # local|remote
    self.readonly = False
    self.placement = "any"  # any|sysvol|nonsysvol
    self.dataset = None

  def _write (self, element):
    bse = ET.SubElement(element, "{%s}blockstore" % (PGNS.EMULAB))
    bse.attrib["name"] = self.name
    bse.attrib["mountpoint"] = self.mount
    bse.attrib["class"] = self.where
    if self.size:
      bse.attrib["size"] = "%dGB" % (self.size)
    bse.attrib["placement"] = self.placement
    if self.readonly:
      bse.attrib["readonly"] = "true"
    if self.dataset:
      if isinstance(self.dataset, (str, unicode)):
        bse.attrib["dataset"] = self.dataset
      elif isinstance(self.dataset, urn.Base):
        bse.attrib["dataset"] = str(self.dataset)
    return bse

pg.Node.EXTENSIONS.append(("Blockstore", Blockstore))


class RemoteBlockstore(pg.Node):
  def __init__ (self, name, mount):
    super(RemoteBlockstore, self).__init__(name, "emulab-blockstore")
    bs = Blockstore("%s-bs" % (self.name), mount)
    bs.where = "remote"
    self._bs = bs
    self._interface = self.addInterface("if0")

  @property
  def interface (self):
    return self._interface

  @property
  def size (self):
    return self._bs.size

  @size.setter
  def size (self, val):
    self._bs.size = val

  @property
  def mountpoint (self):
    return self._bs.mount

  @property
  def dataset (self):
    return self._bs.dataset

  @dataset.setter
  def dataset (self, val):
    self._bs.dataset = val


class Firewall(object):
  class Style(object):
    OPEN     = "open"
    CLOSED   = "closed"
    BASIC    = "basic"

  class Direction(object):
    INCOMING = "incoming"
    OUTGOING = "outgoing"

  def __init__ (self, style):
    self.style = style
    self.exceptions = []

  def addException(self, port, direction, ip = None):
    self.exceptions.append({"port" : port, "direction" : direction, "ip" : ip})

  def _write (self, node):
    fw = ET.SubElement(node, "{%s}firewall" % (PGNS.EMULAB))
    fw.attrib["style"] = self.style
    for excep in self.exceptions:
      ex = ET.SubElement(fw, "exception")
      ex.attrib["port"]      = str(excep["port"])
      ex.attrib["direction"] = excep["direction"]
      if excep["ip"]:
        ex.attrib["ip"] = excep["ip"]
    return fw

XenVM.EXTENSIONS.append(("Firewall", Firewall))


class Tour(object):
  TEXT = "text"
  MARKDOWN = "markdown"

  def __init__ (self):
    self.description = None
    # Type can markdown
    self.description_type = Tour.TEXT
    self.instructions = None
    # Type can markdown
    self.instructions_type = Tour.TEXT

  def Description(self, type, desc):
    self.description_type = type
    self.description = desc

  def Instructions(self, type, inst):
    self.instructions_type = type
    self.instructions = inst

  def _write (self, root):
    #
    # Please do it this way, until some of our JS code is fixed.
    #
    td = ET.SubElement(root, "rspec_tour",
                       nsmap={None : PGNS.TOUR.name})
    if self.description:
      desc = ET.SubElement(td, "description")
      desc.text = self.description
      desc.attrib["type"] = self.description_type
    if self.instructions:
      inst = ET.SubElement(td, "instructions")
      inst.text = self.instructions
      inst.attrib["type"] = self.instructions_type
    return td


class Site(object):
  def __init__ (self, id):
    self.id = id

  def _write (self, node):
    site = ET.SubElement(node, "{%s}site" % (PGNS.JACKS))
    site.attrib["id"] = self.id
    return site

pg.Node.EXTENSIONS.append(("Site", Site))

