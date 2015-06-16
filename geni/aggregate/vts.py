# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import sys
import inspect

from .core import AM, APIRegistry

class VTS(AM):
  def __init__ (self, name, host, url = None):
    self.host = host
    if url is None:
      url = "https://%s:3626/foam/gapi/2" % (host)
    self.urlv3 = "%s3" % (url[:-1])
    self._apiv3 = APIRegistry.get("amapiv3")
    super(VTS, self).__init__(name, url, "amapiv2", "vts")

  def changeController (self, context, sname, url, datapaths):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:change-controller",
                           options={"controller-url" : url, "datapaths" : datapaths})

  def dumpFlows (self, context, sname, datapaths, show_hidden=False):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:dump-flows",
                           options={"datapaths" : datapaths, "show-hidden" : show_hidden})
    

DDC = VTS("vts-ddc", "ddc.vts.bsswks.net")
Clemson = VTS("vts-clemson", "clemson.vts.bsswks.net")
GPO = VTS("vts-gpo", "gpo.vts.bsswks.net")
Illinois = VTS("vts-illinois", "uiuc.vts.bsswks.net")
MAX = VTS("vts-max", "max.vts.bsswks.net")
NPS = VTS("vts-nps", "nps.vts.bsswks.net")
UKYPKS2 = VTS("vts-ukypks2", "ukypks2.vts.bsswks.net")
UtahDDC = DDC
StarLight = VTS("vts-starlight", "starlight.vts.bsswks.net")
UH = VTS("vts-uh", "uh.vts.bsswks.net")
UWashington = VTS("vts-uwashington", "uwash.vts.bsswks.net")


def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj

def name_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      result[obj.name] = obj
  return result
