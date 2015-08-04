# Copyright (c) 2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import requests

import geni._coreutil as GCU

import requests.packages.urllib3
import requests.packages.urllib3.exceptions
requests.packages.urllib3.disable_warnings((requests.packages.urllib3.exceptions.InsecureRequestWarning,
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning))

class ResourceDiscovery(object):
  def __init__ (self, name, host, port = 443, url = None):
    self.name = name
    self.url = url
    if self.url is None:
      self.url = "https://%s:%d" % (host, port)

    self._uid = None
    self._version = None
    self._release = None

  def _populate (self):
    r = requests.get(self.url, **self.rkwargs)
    data = r.json()
    self._uid = data["uid"]
    self._version = data["version"]
    self._release = data["release"]

  @property
  def rkwargs (self):
    d = {"headers" : self.headers,
         "verify" : False}
    return d

  @property
  def headers (self):
    d = {"Content-Type" : "application/json"}
    d.update(GCU.defaultHeaders())
    return d

  @property
  def uid (self):
    if not self._uid:
      self._populate()
    return self._uid

  @property
  def version (self):
    if not self._version:
      self._populate()
    return self._version
    
  @property
  def release (self):
    if not self._release:
      self._populate()
    return self._release

