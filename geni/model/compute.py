# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from geni.model import base

class ComputeDiskImage(base.Image):
  def __init__ (self):
    super(ComputeDiskImage, self).__init__ ()
    self.url = None
    self.os = None
    self.osver = None
    self.arch = None

