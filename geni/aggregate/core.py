# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import os.path

from .. import tempfile

class _Registry(object):
  def __init__ (self):
    self._data = {}

  def register (self, name, obj):
    self._data[name] = obj

  def get (self, name):
    return self._data[name]


class AM(object):
  class UnspecifiedComponentManagerError(Exception):
    def __str__ (self):
      return "AM object does not have a component manager ID specified"

  class InvalidRSpecPathError(Exception):
    def __init__ (self, path):
      super(AM.InvalidRSpecPathError, self).__init__()
      if len(path) > 400:
        path = path[:400] + "..."
      self.path = path
    def __str__ (self):
      return "RSpec object provided as path string, but path not found: %s" % (self.path)


  def __init__ (self, name, url, api, amtype, cmid=None):
    self.url = url
    self.name = name
    self._cmid = cmid
    self._apistr = api
    self._api = None
    self._typestr = amtype
    self._type = None

  @property
  def component_manager_id (self):
    if self._cmid:
      return self._cmid
    raise AM.UnspecifiedComponentManagerError()

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

  def listresources (self, context, slice = None, available = False):
    rspec_data = self.api.listresources(context, self.url, slice, {"geni_available" : available})
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
    if isinstance(rspec, (str, unicode)):
      rspec = os.path.normpath(os.path.expanduser(rspec))
      if not os.path.exists(rspec):
        raise AM.InvalidRSpecPathError(rspec)
      path = rspec
    else:
      (tf, path) = tempfile.makeFile()
      tf.close()
      rspec.writeXML(path)
    res = self.api.createsliver(context, self.url, sname, path)
    os.remove(path)
    return self.amtype.parseManifest(res)

  def getversion (self, context):
    return self.api.getversion(context, self.url)


APIRegistry = _Registry()
AMTypeRegistry = _Registry()
FrameworkRegistry = _Registry()
