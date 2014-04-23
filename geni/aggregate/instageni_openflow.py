# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import sys
import inspect

from .core import AM

class IGOF(AM):
  def __init__ (self, name, host, url = None):
    if url is None:
      url = "https://%s:3626/foam/gapi/2" % (host)
    super(IGOF, self).__init__(name, url, "amapiv2", "foam")

  def listresources (self, context, slice = None):
    rspec_data = self.api.listresources(context, self.url, slice)
    if slice is None:
      return self.amtype.parseAdvertisement(rspec_data)
    else:
      return self.amtype.parseManifest(rspec_data)


CaseWestern = IGOF("ig-of-cwru", "foam.geni.case.edu")
Cornell = IGOF("ig-of-cornell", "foam.geni.it.cornell.edu")
Clemson = IGOF("ig-of-clemson", "foam.instageni.clemson.edu")
Dublin = IGOF("ig-ohmetrodc", "foam.instageni.metrodatacenter.com")
GATech = IGOF("ig-gatech", "foam.instageni.rnoc.gatech.edu")
GPO = IGOF("ig-gpo", "foam.instageni.gpolab.bbn.com")
Illinois = IGOF("ig-illinois", "foam.instageni.illinois.edu")
Kansas = IGOF("ig-kansas", "foam.instageni.ku.gpeni.net")
Kentucky = IGOF("ig-kentucky", "foam.lan.sdn.uky.edu")
Kettering = IGOF("ig-kettering", "foam.geni.kettering.edu")
LSU = IGOF("ig-lsu", "foam.instageni.lsu.edu")
MAX = IGOF("ig-max", "foam.instageni.maxgigapop.net")
Missouri = IGOF("ig-missouri", "foam.instageni.rnet.missouri.edu")
MOXI = IGOF("ig-moxi", "foam.instageni.iu.edu")
Northwestern = IGOF("ig-northwestern", "foam.instageni.northwestern.edu")
NPS = IGOF("ig-nps", "foam.instageni.nps.edu")
NYSERNet = IGOF("ig-nysernet", "foam.instageni.nysernet.org")
NYU = IGOF("ig-nyu", "foam.genirack.nyu.edu")
Princeton = IGOF("ig-princeton", "foam.instageni.cs.princeton.edu")
Rutgers = IGOF("ig-rutgers", "foam.instageni.rutgers.edu")
SOX = IGOF("ig-sox", "foam.instageni.sox.net")
Stanford = IGOF("ig-stanford", "foam.instageni.stanford.edu")
Utah = IGOF("ig-utah", "foam.utah.geniracks.net")
UtahDDC = IGOF("ig-utahddc", "foam.utahddc.geniracks.net")
Wisconsin = IGOF("ig-wisconsin", "foam.instageni.wisc.edu")


def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
