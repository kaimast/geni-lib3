# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class IGCompute(AM):
  def __init__ (self, name, url):
    super(IGCompute, self).__init__(name, url, "amapiv2", "pg")

  def listresources (self, context, slice = None):
    rspec_data = self.api.listresources(context, self.url, slice)
    if slice is None:
      return self.framework.parseAdvertisement(rspec_data)
    else:
      return self.framework.parseManifest(rspec_data)


GPO = IGCompute("ig-gpo", "https://boss.instageni.gpolab.bbn.com:12369/protogeni/xmlrpc/am/2.0")
Kentucky = IGCompute("ig-kentucky", "https://boss.lan.sdn.uky.edu:12369/protogeni/xmlrpc/am/2.0")
Utah = IGCompute("ig-utah", "https://boss.utah.geniracks.net:12369/protogeni/xmlrpc/am/2.0")
UtahDDC = IGCompute("ig-utahddc", "https://boss.utahddc.geniracks.net:12369/protogeni/xmlrpc/am/2.0")

def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
