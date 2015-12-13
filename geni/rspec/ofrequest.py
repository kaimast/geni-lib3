# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from . import RSpec

class Request(RSpec):
  def __init__ (self):
    super(Request, self).__init__("request")
    self.resources = []

  def addGroup (self, name):
    group = Group(name)
    self.resources.append(group)
    return group

  def buildMatch (self):
    match = Match()
    self.resources.append(match)
    return match

class Datapath(object):
  def __init__ (self, ad_dp = None):
    self._ad_dp = ad_dp
