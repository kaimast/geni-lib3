# Copyright (c) 2014  Barnstormer Softworks, Ltd.

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
  def __init__ (self, *args, **kwargs):
    super(RemoteBlockstore, self).__init__(*args, **kwargs)
    self.type = "emulab-blockstore"
    bs = self.Blockstore("%s-bs" % (self.name), None)
    bs.where = "remote"
    self._bs = bs
    self.interface = self.addInterface("if0")

  @property
  def mountpoint (self, val):
    self._bs.mount = val

  @property
  def dataset (self, val):
    self._bs.dataset = val
