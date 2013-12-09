# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import inspect
import sys

from . import AM

class PGAM(AM):
  def __init__ (self, name, url):
    super(IGCompute, self).__init__(name, url, "amapiv2", "pg")

GPO = PGAM("ig-gpo", "https://boss.instageni.gpolab.bbn.com:12369/protogeni/xmlrpc/am/2.0")
Kentucky = PGAM("ig-kentucky", "https://boss.lan.sdn.uky.edu:12369/protogeni/xmlrpc/am/2.0")
Utah = PGAM("ig-utah", "https://boss.utah.geniracks.net:12369/protogeni/xmlrpc/am/2.0")
UtahDDC = PGAM("ig-utahddc", "https://boss.utahddc.geniracks.net:12369/protogeni/xmlrpc/am/2.0")

def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
