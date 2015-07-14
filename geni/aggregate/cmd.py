# Copyright (c) 2013-2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

def listresources (user, am, slice = None):
  from ..gcf import oscript
  text, res = oscript.call(["-a", am, "listresources"])
  if res.values()[0]["code"]["geni_code"] == 0:
    rspec = res.values()[0]["value"]
    return rspec


def getusercred (cfg_path):
  from ..gcf import oscript
  text, cred = oscript.call(["-c", cfg_path, "getusercred"])
  return cred


def getslicecred (context, sname):
  from ..gcf import oscript
  arglist = ["-c", context.cfg_path, "--usercredfile", context.usercred_path, "getslicecred", sname]
  if context.debug:
    arglist.insert(0, "--debug")
  else:
    arglist.insert(0, "--warn")

  text, cred = oscript.call(arglist)
  return (text,cred)


def renewsliver (am, slice, t):
  pass
