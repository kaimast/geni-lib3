# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import json

from .core import APIRegistry
from .. import tempfile

class AMError(Exception):
  def __init__ (self, text, data = None):
    super(AMError, self).__init__()
    self.text = text
    self.data = data
  def __str__ (self):
    return self.text

class DeleteSliverError(AMError): pass
class CreateSliverError(AMError): pass
class SliverStatusError(AMError): pass
class RenewSliverError(AMError): pass
class ListResourcesError(AMError): pass

class AMAPIv3(object):
  def _getDefaultArgs (self, context, url):
    return ["--warn", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "--usercredfile",
            context.usercred_path, "-a", url, "-V", "3"]

  def poa (self, context, url, sname, action, options = None):
    from ..minigcf import amapi3 as AM3

    sinfo = context.getSliceInfo(sname)
    res = AM3.poa(url, False, context.cf.cert, context.cf.key, [sinfo], [sinfo.urn], action, options)
    if res["code"]["geni_code"] == 0:
      return res["value"]

    # TODO: Raise exception


class AMAPIv2(object):
  def _getDefaultArgs (self, context, url):
    if context.debug:
      return ["--debug", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "--usercredfile",
              context.usercred_path, "-a", url, "-V", "2"]
    else:
      return ["--warn", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "--usercredfile",
              context.usercred_path, "-a", url, "-V", "2"]

  def listresources (self, context, url, sname, options = None):
    if not options: options = {}

    from ..minigcf import amapi2 as AM2
    creds = []

    surn = None
    if sname:
      sinfo = context.getSliceInfo(sname)
      surn = sinfo.urn
      creds.append(open(sinfo.path, "rb").read())

    creds.append(open(context.usercred_path, "rb").read())

    res = AM2.listresources(url, False, context.cf.cert, context.cf.key, creds, options, surn)
    if res["code"]["geni_code"] == 0:
      return res

    raise ListResourcesError(res["output"], res)


  def createsliver (self, context, url, sname, rspec):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "createsliver", sname, rspec])
    text,res = oscript.call(arglist)
    if res is None:
      raise CreateSliverError(text)
    return res

  def sliverstatus (self, context, url, sname):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "sliverstatus", sname])
    text, res = oscript.call(arglist)
    if not res.values()[0]:
      raise SliverStatusError(text)
    return res.values()[0]

  def renewsliver (self, context, url, sname, date):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "renewsliver", sname, str(date)])
    text, res = oscript.call(arglist)
    if res[1]:
      raise RenewSliverError(text)
    return (text, res)

  def deletesliver (self, context, url, sname):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "deletesliver", sname])
    text,res = oscript.call(arglist)
    if res[1]:
      raise DeleteSliverError(text)

  def getversion (self, context, url):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["getversion"])
    _,res = oscript.call(arglist)
    return res.values()[0]


class AMAPIv1(object):
  def _getDefaultArgs (self, context, url):
    if context.debug:
      return ["--debug", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "--usercredfile",
              context.usercred_path, "-a", url, "-V", "1"]
    else:
      return ["--warn", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "--usercredfile",
              context.usercred_path, "-a", url, "-V", "1"]

  def listresources (self, context, url, sname):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)

    if sname:
      arglist.extend(["--slicecredfile", context.slicecreds[sname], "listresources", sname])
    else:
      arglist.append("listresources")

    text,res = oscript.call(arglist)
    if res.values()[0] and res.values()[0] != "":
      rspec = res.values()[0]
      return rspec
    else:
      raise ListResourcesError(text)

  def createsliver (self, context, url, sname, rspec):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "createsliver", sname, rspec])
    text,res = oscript.call(arglist)
    if res is None:
      raise CreateSliverError(text)
    return res

  def sliverstatus (self, context, url, sname):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "sliverstatus", sname])
    text, res = oscript.call(arglist)
    if not res.values()[0]:
      raise SliverStatusError(text)
    return res.values()[0]

  def renewsliver (self, context, url, sname, date):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "renewsliver", sname, str(date)])
    text, res = oscript.call(arglist)
    if res[1]:
      raise RenewSliverError(text)
    return (text, res)

  def deletesliver (self, context, url, sname):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["--slicecredfile", context.slicecreds[sname], "deletesliver", sname])
    text,res = oscript.call(arglist)
    if res[1]:
      raise DeleteSliverError(text)

  def getversion (self, context, url):
    from ..gcf import oscript
    arglist = self._getDefaultArgs(context, url)
    arglist.extend(["getversion"])
    _,res = oscript.call(arglist)
    return res.values()[0]

APIRegistry.register("amapiv1", AMAPIv1())
APIRegistry.register("amapiv2", AMAPIv2())
APIRegistry.register("amapiv3", AMAPIv3())

