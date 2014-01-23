# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

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
      return self.type.parseAdvertisement(rspec_data)
    else:
      return self.type.parseManifest(rspec_data)

  def sliverstatus (self, context, sname):
    status = self.api.sliverstatus(context, self.url, sname)


class IGOpenflow(AM):
  def __init__ (self, name, url):
    super(IGOpenflow, self).__init__(name, url, "amapiv2", "foam")


Clemson = IGCompute("ig-clemson", "https://instageni.clemson.edu:12369/protogeni/xmlrpc/am/2.0")
GATech = IGCompute("ig-gatech", "https://instageni.rnoc.gatech.edu:12369/protogeni/xmlrpc/am/2.0")
GPO = IGCompute("ig-gpo", "https://boss.instageni.gpolab.bbn.com:12369/protogeni/xmlrpc/am/2.0")
Illinois = IGCompute("ig-illinois", "https://instageni.illinois.edu:12369/protogeni/xmlrpc/am/2.0")
Kentucky = IGCompute("ig-kentucky", "https://boss.lan.sdn.uky.edu:12369/protogeni/xmlrpc/am/2.0")
Kettering = IGCompute("ig-kettering", "https://geni.kettering.edu:12369/protogeni/xmlrpc/am/2.0")
MAX = IGCompute("ig-max", "https://instageni.maxgigapop.net:12369/protogeni/xmlrpc/am/2.0")
Missouri = IGCompute("ig-missouri", "https://instageni.rnet.missouri.edu:12369/protogeni/xmlrpc/am/2.0")
Northwestern = IGCompute("ig-northwestern", "https://instageni.northwestern.edu:12369/protogeni/xmlrpc/am/2.0")
NYSERNet = IGCompute("ig-nysernet", "https://instageni.nysernet.org:12369/protogeni/xmlrpc/am/2.0")
NYU = IGCompute("ig-nyu", "https://genirack.nyu.edu:12369/protogeni/xmlrpc/am/2.0")
Utah = IGCompute("ig-utah", "https://boss.utah.geniracks.net:12369/protogeni/xmlrpc/am/2.0")
UtahDDC = IGCompute("ig-utahddc", "https://boss.utahddc.geniracks.net:12369/protogeni/xmlrpc/am/2.0")
Wisconsin = IGCompute("ig-wisconsin", "https://instageni.wisc.edu:12369/protogeni/xmlrpc/am/2.0")

def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
