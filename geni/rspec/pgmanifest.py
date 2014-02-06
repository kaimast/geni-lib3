# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET
from geni.rspec.pg import Link
import geni.namespaces as GNS

class ManifestLink(Link):
  def __init__ (self):
    super(ManifestLink, self).__init__(self)

  @classmethod
  def _fromdom (cls, elem):
    lnk = ManifestLink()
    lnk.client_id = elem.get("client_id")
    lnk.sliver_id = elem.get("sliver_id")
    lnk.vlan = elem.get("vlantag", None)

    return lnk


class Manifest(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def links (self):
    for link in self._root.findall("{%s}link" % (GNS.REQUEST.name)):
      yield ManifestLink._fromdom(link)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
