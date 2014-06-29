# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import sys
import inspect

from .core import AM

class OF(AM):
  def __init__ (self, name, host, url = None):
    if url is None:
      url = "https://%s:3626/foam/gapi/2" % (host)
    super(OF, self).__init__(name, url, "amapiv2", "foam")


Internet2 = OF("of-i2", "foam.net.internet2.edu")
UEN = OF("of-uen", "foamyflow.chpc.utah.edu")


def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
