# Copyright (c) 2015-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Streamlined implementation of xmlrpc calls to AM API v3-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

from __future__ import absolute_import

import xmlrpclib
import ssl

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from .. import _coreutil as GCU
from . import config

GCU.disableUrllibWarnings()

class TLS1HttpAdapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                   block = block, ssl_version = ssl.PROTOCOL_TLSv1)

def headers ():
  return GCU.defaultHeaders()

def getversion (url, root_bundle, cert, key, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps(options, methodname="GetVersion")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)

  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)

  return xmlrpclib.loads(resp.content)[0][0]

def poa (url, root_bundle, cert, key, creds, urns, action, options = None):
  if not options: options = {}
  if not isinstance(urns, list): urns = [urns]

  cred_list = []
  for cred in creds:
    cred_list.append({"geni_value" : open(cred.path, "rb").read(), "geni_type" : cred.type, "geni_version" : cred.version})

  req_data = xmlrpclib.dumps((urns, cred_list, action, options),
                             methodname="PerformOperationalAction")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)

  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)

  return xmlrpclib.loads(resp.content)[0][0]


