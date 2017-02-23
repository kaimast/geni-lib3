# Copyright (c) 2014-2015 Barnstomer Softworks, Ltd. and The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import inspect
import sys

from .core import AM

# Imports to pick up aggregates available in the cloudlab UI
from .instageni import UtahDDC # pylint: disable=unused-import
from .apt import Apt # pylint: disable=unused-import

class CloudLabAM(AM):
  def __init__ (self, name, host, cmid = None, url = None):
    if url is None:
      url = "https://%s:12369/protogeni/xmlrpc/am/2.0" % (host)
    super(CloudLabAM, self).__init__(name, url, "amapiv2", "pg", cmid)


Clemson = CloudLabAM("cl-clemson", "boss.clemson.cloudlab.us", "urn:publicid:IDN+clemson.cloudlab.us+authority+cm")
Utah = CloudLabAM("cl-utah", "boss.utah.cloudlab.us", "urn:publicid:IDN+utah.cloudlab.us+authority+cm")
Wisconsin = CloudLabAM("cl-wisconsin", "www.wisc.cloudlab.us", "urn:publicid:IDN+wisc.cloudlab.us+authority+cm")

def aggregates ():
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, PGCompute):
      yield obj

def name_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, PGCompute):
      result[obj.name] = obj
  return result
