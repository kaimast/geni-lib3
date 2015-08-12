# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Extensions for CloudLab"""

from __future__ import absolute_import

from lxml import etree as ET

from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from . import pg
from .. import urn

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
