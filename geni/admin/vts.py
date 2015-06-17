# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import json

from . import germ

class Connection(germ.Connection):
  def __init__ (self):
    super(Connection, self).__init__()
    self.user = "foamadmin"

  @property
  def pgvlans (self):
    url = "https://%s:%d/core/admin/vts/pgvlans" % (self.host, self.port)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  @property
  def slivers (self):
    url = "https://%s:%d/core/admin/vts/slivers" % (self.host, self.port)
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

  def setSSLVPNIP (self, ipstr):
    url = "https://%s:%d/core/admin/vts/vf/sslvpn/local-ip" % (self.host, self.port)
    d = json.dumps(ipstr)
    r = requests.post(url, d, **self.rkwargs)

  def addCircuitPlane (self, typ, label, endpoint, mtu, types = [], encoded = True):
    url = "https://%s:%d/core/admin/vts/circuitplane/%s" % (
          self.host, self.port, typ)
    d = json.dumps({"label" : label, "endpoint" : endpoint,
                    "supported-types" : types, "encoded" : encoded, "mtu" : mtu})
    r = requests.put(url, d, **self.rkwargs)
    return r

  def getDatapaths (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/datapaths" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def getRequestRspec (self, sliver_urn):
    url = "https://%s:%d/core/admin/vts/sliver/%s/request-rspec" % (self.host, self.port, sliver_urn)
    r = requests.get(url, **self.rkwargs)
    return r.json()["value"]

  def removePort (self, sliver_urn, dpname, client_id):
    url = "https://%s:%d/core/admin/vts/sliver/%s/datapath/%s/port/%s" % (self.host, self.port,
            sliver_urn, dpname, client_id)
    r = requests.delete(url, **self.rkwargs)
    return r.json()["value"]

  def addPGLocal (self, sliver_urn, dpname, client_id, pgcircuit):
    url = "https://%s:%d/core/admin/vts/sliver/%s/datapath/%s/port/%s" % (self.host, self.port,
            sliver_urn, dpname, client_id)
    d = json.dumps({"type" : "pg-local", "shared-lan" : pgcircuit})
    r = requests.put(url, d, **self.rkwargs)
    return r.json()["value"]

  def addImage (self, image_name):
    url = "https://%s:%d/core/admin/vts/image" % (self.host, self.port)
    d = json.dumps({"name" : image_name})
    r = requests.post(url, d, **self.rkwargs)
    return r.json()["value"]
