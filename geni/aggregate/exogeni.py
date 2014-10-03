# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class EGCompute(AM):
  def __init__ (self, name, host, url = None):
    if url is None:
      url = "https://%s:11443/orca/xmlrpc" % (host)
    super(EGCompute, self).__init__(name, url, "amapiv2", "pg")

EXOSM = EGCompute("exosm", "geni.renci.org")
GPO = EGCompute("eg-gpo", "bbn-hn.exogeni.net")
RCI = EGCompute("eg-rci", "rci-hn.exogeni.net")
FIU = EGCompute("eg-fiu", "fiu-hn.exogeni.net")
UH = EGCompute("eg-uh", "uh-hn.exogeni.net")
NCSU = EGCompute("eg-ncsu", "ncsu-hn.exogeni.net")
UFL = EGCompute("eg-ufl", "ufl-hn.exogeni.net")
OSF = EGCompute("eg-osf", "osf-hn.exogeni.net")
UCD = EGCompute("eg-ucd", "ucd-hn.exogeni.net")

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
