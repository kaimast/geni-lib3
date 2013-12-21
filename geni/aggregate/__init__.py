# Copyright (c) 2013  Barnstormer Softworks

class _Registry(object):
  def __init__ (self):
    self._data = {}

  def register (self, name, obj):
    self._data[name] = obj

  def get (self, name):
    return self._data[name]


class AM(object):
  def __init__ (self, name, url, api, framework):
    self.url = url
    self.name = name
    self._apistr = api
    self._api = None
    self._frameworkstr = framework
    self._framework = None

  @property
  def api (self):
    if not self._api:
      self._api = APIRegistry.get(self._apistr)
    return self._api

  @property
  def framework (self):
    if not self._framework:
      self._framework = FrameworkRegistry.get(self._frameworkstr)
    return self._framework


APIRegistry = _Registry()
FrameworkRegistry = _Registry()

class AMAPIv2(object):
  def _getDefaultArgs (self, context, url):
    return ["-c", context.cfg_path, "--usercredfile", context.usercred_path, "-a", url, "-V", "2"]

  def listresources (self, context, url, slice):
    arglist = self._getDefaultArgs(context, url)

    if slice:
      arglist.extend(["--slicecredfile", context.slicecred_path, "listresources", slice])
    else:
      arglist.append("listresources")

    text,res = oscript.call(arglist)
    if res.values()[0]["code"]["geni_code"] == 0:
      rspec = res.values()[0]["value"]
      return rspec


