# Copyright (c) 2013  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import inspect
import sys

from . import AM

GPO = AM("ig-gpo", "https://boss.instageni.gpolab.bbn.com:12369/protogeni/xmlrpc/am/2.0", "amapiv2", "pg")
Kentucky = AM("ig-kentucky", "https://boss.lan.sdn.uky.edu:12369/protogeni/xmlrpc/am/2.0", "amapiv2", "pg")
Utah = AM("ig-utah", "https://boss.utah.geniracks.net:12369/protogeni/xmlrpc/am/2.0", "amapiv2", "pg")
UtahDDC = AM("ig-utahddc", "https://boss.utahddc.geniracks.net:12369/protogeni/xmlrpc/am/2.0", "amapiv2", "pg")

def aggregates ():
  module = sys.modules[__name__]
  for name,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj
