# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

from ..gcf import oscript
from .core import APIRegistry

class AMError(Exception):
  def __init__ (self, text):
    self.text = text
  def __str__ (self):
    return self.text
  
class DeleteSliverError(AMError): pass
class CreateSliverError(AMError): pass
class SliverStatusError(AMError): pass


class AMAPIv2(object):
  def _getDefaultArgs (self, context, url):
    if context.debug:
      return ["--debug", "-c", context.cfg_path, "--usercredfile", context.usercred_path, "-a", url, "-V", "2"]
    else:
      return ["--warn", "-c", context.cfg_path, "--usercredfile", context.usercred_path, "-a", url, "-V", "2"]

  def listresources (self, context, url, sname):
    arglist = self._getDefaultArgs(context, url)

    if sname:
      arglist.extend(["--slicecredfile", context.slicecreds[sname], "listresources", sname])
    else:
      arglist.append("listresources")

    print arglist
    text,res = oscript.call(arglist)
    if res.values()[0]["code"]["geni_code"] == 0:
      rspec = res.values()[0]["value"]
      return rspec

  def createsliver (self, context, url, sname, rspec):
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "createsliver", sname, rspec])
    text,res = oscript.call(arglist)
    if res is None:
      raise CreateSliverError(text)
    return res

  def sliverstatus (self, context, url, sname):
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "sliverstatus", sname])
    text, res = oscript.call(arglist)
    if not res.values()[0]:
      raise SliverStatusError(text)
    return res.values()[0]

  def renewsliver (self, context, url, sname, date):
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "renewsliver", sname, str(date)])
    text, res = oscript.call(arglist)
    return text,res

  def deletesliver (self, context, url, sname):
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "deletesliver", sname])
    text,res = oscript.call(arglist)
    if res[1]:
      raise DeleteSliverError(text)


APIRegistry.register("amapiv2", AMAPIv2())

