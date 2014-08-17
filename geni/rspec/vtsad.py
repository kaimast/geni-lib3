# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from lxml import etree as ET

class Advertisement(object):
  def __init__ (self, path = None, xml = None):
    if path:
      self._root = ET.parse(open(path))
    elif xml:
      self._root = ET.fromstring(xml)

  @property
  def text (self):
    return ET.tostring(self._root, pretty_print=True)
