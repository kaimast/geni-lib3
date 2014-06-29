# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import tempfile
import os

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
    self._urn_prefix = None
    self._apistr = api
    self._api = None
    self._typestr = amtype
    self._type = None

  @property
  def component_manager_id (self):
    return "%s+authority+am" % (self._urn_prefix)

  @property
  def api (self):
    if not self._api:
      self._api = APIRegistry.get(self._apistr)
    return self._api

  @property
  def amtype (self):
    if not self._type:
      self._type = AMTypeRegistry.get(self._typestr)
    return self._type

  def listresources (self, context, slice = None):
    rspec_data = self.api.listresources(context, self.url, slice)
    if slice is None:
      return self.amtype.parseAdvertisement(rspec_data)
    else:
      return self.amtype.parseManifest(rspec_data)

  def sliverstatus (self, context, sname):
    status = self.api.sliverstatus(context, self.url, sname)
    return status

  def renewsliver (self, context, sname, date):
    text,res = self.api.renewsliver(context, self.url, sname, date)
    return text,res

  def deletesliver (self, context, sname):
    self.api.deletesliver(context, self.url, sname)

  def createsliver (self, context, sname, rspec):
    tf = tempfile.NamedTemporaryFile(delete=False)
    path = tf.name
    tf.close()
    rspec.write(path)
    res = self.api.createsliver(context, self.url, sname, path)
    os.remove(path)
    return self.amtype.parseManifest(res)


APIRegistry = _Registry()
AMTypeRegistry = _Registry()
FrameworkRegistry = _Registry()
