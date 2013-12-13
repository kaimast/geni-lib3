# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

class Image(object):
  def __init__ (self):
    self.id = None
    self.urn = None


class ImageRegistry(object):
  def __init__ (self):
    self._data = {}

  def register (self, manager, image):
    self._data.getdefault(image.id, {})[manager] = image
