# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

import os

class Context (object):

  def __init__ (self):
    if 'GENILIB_PORTAL_MODE' in os.environ:
      self._standalone = False
      self._portalRequestPath = os.environ['GENILIB_PORTAL_REQUEST_PATH']
    else:
      self._standalone = True
      self._portalRequestPath = None

  def printRequestRSpec (self, rspec):
    rspec.writeXML(self._portalRequestPath)

