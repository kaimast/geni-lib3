# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

class PGCompute(AM):
  def __init__ (self, name, host, cmid = None, url = None):
    if url is None:
      url = "https://%s:12369/protogeni/xmlrpc/am/2.0" % (host)
    super(PGCompute, self).__init__(name, url, "amapiv2", "pg", cmid)

Kentucky_PG = PGCompute('pg-kentucky', 'www.uky.emulab.net', 'urn:publicid:IDN+uky.emulab.net+authority+cm')
UTAH_PG = PGCompute('pg-utah', 'www.emulab.net', 'urn:publicid:IDN+emulab.net+authority+cm');
Wall2_PG = PGCompute("pg-wall2", "www.wall2.ilabt.iminds.be", "urn:publicid:IDN+wall2.ilabt.iminds.be+authority+cm")
Wall1_PG = PGCompute("pg-wall1", "www.wall1.ilabt.iminds.be", "urn:publicid:IDN+wall1.ilabt.iminds.be+authority+cm")
wilab_PG = PGCompute("pg-wilab", "www.wilab2.ilabt.iminds.be", "urn:publicid:IDN+wilab2.ilabt.iminds.be+authority+cm")

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
