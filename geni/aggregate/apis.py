# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from .core import APIRegistry

class AMAPIv2(object):
  def _getDefaultArgs (self, context, url):
    return ["-c", context.cfg_path, "--usercredfile", context.usercred_path, "-a", url, "-V", "2"]

  def listresources (self, context, url, sname):
    arglist = self._getDefaultArgs(context, url)

    if slice:
      arglist.extend(["--slicecredfile", context.slicecred_paths[sname], "listresources", sname])
    else:
      arglist.append("listresources")

    text,res = oscript.call(arglist)
    if res.values()[0]["code"]["geni_code"] == 0:
      rspec = res.values()[0]["value"]
      return rspec

APIRegistry.register("amapiv2", AMAPIv2())


