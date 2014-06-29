# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import sys
import inspect

from .core import AM

class VTS(AM):
  def __init__ (self, name, host, url = None):
    if url is None:
      url = "https://%s:3626/foam/gapi/2" % (host)
    super(VTS, self).__init__(name, url, "amapiv2", "vts")

DDC = VTS("vts-ddc", "ddc.vts.bsswks.net")
Illinois = VTS("vts-illinois", "uiuc.vts.bsswks.net")
MAX = VTS("vts-max", "max.vts.bsswks.net")
GPO = VTS("vts-gpo", "gpo.vts.bsswks.net")


def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
