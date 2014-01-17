# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from ..gcf import oscript

def listresources (user, am, slice = None):
  text, res = oscript.call(["-a", am, "listresources"])
  if res.values()[0]["code"]["geni_code"] == 0:
    rspec = res.values()[0]["value"]
    return rspec

def getusercred (cfg_path):
  text, cred = oscript.call(["-c", cfg_path, "getusercred"])
  return cred

def renewsliver (am, slice, t):
  pass
