# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from .core import APIRegistry

class AMError(Exception):
  def __init__ (self, text, data = None):
    super(AMError, self).__init__()
    self.text = text
    self.data = data
  def __str__ (self):
    return self.text

class GetVersionError(AMError): pass
class DeleteSliverError(AMError): pass
class CreateSliverError(AMError): pass
class SliverStatusError(AMError): pass
class RenewSliverError(AMError): pass
class ListResourcesError(AMError): pass


class AMAPIv3(object):
  @staticmethod
  def poa (context, url, sname, action, options = None):
    from ..minigcf import amapi3 as AM3

    sinfo = context.getSliceInfo(sname)
    res = AM3.poa(url, False, context.cf.cert, context.cf.key, [sinfo], [sinfo.urn], action, options)
    if res["code"]["geni_code"] == 0:
      return res["value"]

    # TODO: Raise exception


class AMAPIv2(object):
  @staticmethod
  def listresources (context, url, sname, options = None):
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

  @staticmethod
  def createsliver (context, url, sname, rspec):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "rb").read()

    udata = []
    for user in context._users:
      data = {"urn" : user.urn, "keys" : [open(x, "rb").read() for x in user._keys]}
      udata.append(data)

    res = AM2.createsliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn, rspec, udata)
    if res["code"]["geni_code"] == 0:
      return res
    raise CreateSliverError(res["output"], res)

  @staticmethod
  def sliverstatus (context, url, sname):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "rb").read()
    res = AM2.sliverstatus(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise SliverStatusError(res["output"], res)

  @staticmethod
  def renewsliver (context, url, sname, date):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "rb").read()
    res = AM2.renewsliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn, date)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise RenewSliverError(res["output"], res)

  @staticmethod
  def deletesliver (context, url, sname):
    from ..minigcf import amapi2 as AM2

    sinfo = context.getSliceInfo(sname)
    cred_data = open(sinfo.path, "rb").read()
    res = AM2.deletesliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise DeleteSliverError(res["output"], res)

  @staticmethod
  def getversion (context, url):
    from ..minigcf import amapi2 as AM2

    res = AM2.getversion(url, False, context.cf.cert, context.cf.key)
    if res["code"]["geni_code"] == 0:
      return res["value"]
    raise GetVersionError(res["output"], res)


APIRegistry.register("amapiv2", AMAPIv2())
APIRegistry.register("amapiv3", AMAPIv3())

