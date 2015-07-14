# Copyright (c) 2014 Barnstomer Softworks, Ltd. and The University of Utah

from __future__ import absolute_import

import inspect
import sys

from .core import AM
from .instageni import UtahDDC

class AptAM(AM):
  def __init__ (self, name, host, cmid = None, url = None):
    if url is None:
      url = "https://%s:12369/protogeni/xmlrpc/am/2.0" % (host)
    super(AptAM, self).__init__(name, url, "amapiv2", "pg", cmid)


Apt = AptAM("apt", "boss.apt.emulab.net", "urn:publicid:IDN+boss.apt.emulab.net+authority+cm")

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
