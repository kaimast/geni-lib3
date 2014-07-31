# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import requests
import requests.auth

class Connection(object):
  def __init__ (self):
    self.user = "foamadmin"
    self.password = None
    self.host = "localhost"
    self.port = 3626

  @property
  def rkwargs (self):
    d = {"headers" : self.headers,
         "auth" : self.auth,
         "verify" : False}
    return d

  @property
  def headers (self):
    return {"Content-Type" : "application/json"}

  @property
  def auth (self):
    return requests.auth.HTTPBasicAuth(self.user, self.password)

  @property
  def pgvlans (self):
    url = "https://%s:%d/core/admin/vts/pgvlans" % (self.host, self.port)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def addTargetBridge (self, name, brname):
    url = "https://%s:%d/core/admin/vts/target-bridge" % (self.host, self.port)
    d = json.dumps({"name" : name, "brname" : brname})
    r = requests.post(url, d, **self.rkwargs)

  def addPGVlan (self, name, vid):
    url = "https://%s:%d/core/admin/vts/pgvlan" % (self.host, self.port)
    d = json.dumps({"name" : name, "vid" : vid})
    r = requests.post(url, d, **self.rkwargs)
