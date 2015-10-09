# Copyright (c) 2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from . import pg
from . import stitching
from ..model.util import XPathXRange

_XPNS = {'g' : GNS.REQUEST.name, 'e' : PGNS.EMULAB.name, 't' : stitching.STITCHNS.name}

class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def stitchinfo (self):
    """Reference to the stitching info in the manifest, if present."""
    try:
      elem = self._root.xpath('/g:rspec/t:stitching', namespaces=_XPNS)[0]
      return stitching.AdInfo(elem)
    except IndexError:
      return None

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
