# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from .core import AM

class IGOF(AM):
  def __init__ (self, name, host, url = None):
    if url is None:
      url = "https://%s:3626/foam/gapi/2"
    super(IGOF, self).__init__(name, url, "amapiv2", "foam")

  def listresources (self, context, slice = None):
    rspec_data = self.api.listresources(context, self.url, slice)
    if slice is None:
      return self.amtype.parseAdvertisement(rspec_data)
    else:
      return self.amtype.parseManifest(rspec_data)


def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
