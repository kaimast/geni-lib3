# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

import os

class Context (object):

  def __init__ (self):
    if os.env['GENI-LIB-PORTAL-MODE']:
      self._standalone = False
      self._portalRequestPath = os.env['GENI-LIB-PORTAL-REQUEST-PATH']
    else:
      self._standalone = True
      self._portalRequestPath = None
