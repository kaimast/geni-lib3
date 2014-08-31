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


CaseWestern = IGOF("ig-of-cwru", "foam.geni.case.edu")
Cornell = IGOF("ig-of-cornell", "foam.geni.it.cornell.edu")
Clemson = IGOF("ig-of-clemson", "foam.instageni.clemson.edu")
Dublin = IGOF("ig-of-ohmetrodc", "foam.instageni.metrodatacenter.com")
GATech = IGOF("ig-of-gatech", "foam.instageni.rnoc.gatech.edu")
GPO = IGOF("ig-of-gpo", "foam.instageni.gpolab.bbn.com")
Illinois = IGOF("ig-of-illinois", "foam.instageni.illinois.edu")
Kansas = IGOF("ig-of-kansas", "foam.instageni.ku.gpeni.net")
Kentucky = IGOF("ig-of-kentucky", "foam.lan.sdn.uky.edu")
Kettering = IGOF("ig-of-kettering", "foam.geni.kettering.edu")
LSU = IGOF("ig-of-lsu", "foam.instageni.lsu.edu")
MAX = IGOF("ig-of-max", "foam.instageni.maxgigapop.net")
Missouri = IGOF("ig-of-missouri", "foam.instageni.rnet.missouri.edu")
MOXI = IGOF("ig-of-moxi", "foam.instageni.iu.edu")
Northwestern = IGOF("ig-of-northwestern", "foam.instageni.northwestern.edu")
NPS = IGOF("ig-of-nps", "foam.instageni.nps.edu")
NYSERNet = IGOF("ig-of-nysernet", "foam.instageni.nysernet.org")
NYU = IGOF("ig-of-nyu", "foam.genirack.nyu.edu")
Princeton = IGOF("ig-of-princeton", "foam.instageni.cs.princeton.edu")
Rutgers = IGOF("ig-of-rutgers", "foam.instageni.rutgers.edu")
SOX = IGOF("ig-of-sox", "foam.instageni.sox.net")
Stanford = IGOF("ig-of-stanford", "foam.instageni.stanford.edu")
UCLA = IGOF("ig-of-ucla", "foam.instageni.idre.ucla.edu")
Utah = IGOF("ig-of-utah", "foam.utah.geniracks.net")
UtahDDC = IGOF("ig-of-utahddc", "foam.utahddc.geniracks.net")
Wisconsin = IGOF("ig-of-wisconsin", "foam.instageni.wisc.edu")


def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
