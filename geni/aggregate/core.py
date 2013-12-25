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
      self._framework = FrameworkRegistry.get(self._frameworkstr)()
    return self._framework


APIRegistry = _Registry()
FrameworkRegistry = _Registry()
