# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

class _Registry(object):
  def __init__ (self):
    self._data = {}

  def register (self, name, obj):
    self._data[name] = obj

  def get (self, name):
    return self._data[name]


class AM(object):
  def __init__ (self, name, url, api, amtype):
    self.url = url
    self.name = name
    self._apistr = api
    self._api = None
    self._typestr = framework
    self._type = None

  @property
  def api (self):
    if not self._api:
      self._api = APIRegistry.get(self._apistr)
    return self._api

  @property
  def amtype (self):
    if not self._type:
      self._type = AMTypeRegistry.get(self._typestr)()
    return self._type


APIRegistry = _Registry()
AMTypeRegistry = _Registry()
FrameworkRegistry = _Registry()
