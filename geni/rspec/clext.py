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

class Blockstore(object):
  def __init__ (self, name, size, mount):
    """Creates a BlockStore object with the given name (arbitrary), size (in gigabytes), and mountpoint."""
    self.name = name
    self.size = size
    self.mount = mount
    self._class = "local"

  def _write (self, element):
    bse = ET.SubElement(element, "{%s}blockstore" % (PGNS.EMULAB))
    bse.attrib["name"] = self.name
    bse.attrib["size"] = "%dGB" % (self.size)
    bse.attrib["mountpoint"] = self.mount
    bse.attrib["class"] = self._class
    return bse

pg.Node.EXTENSIONS.append(("Blockstore", Blockstore))
