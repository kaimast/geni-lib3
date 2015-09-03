# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# Streamlined implementation of xmlrpc calls to AM API v3-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

from __future__ import absolute_import

import xmlrpclib
import ssl

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from .. import _coreutil as GCU

# We need to suppress warnings that assume we want a level of security we aren't actually asking for
import requests.packages.urllib3
import requests.packages.urllib3.exceptions
requests.packages.urllib3.disable_warnings((requests.packages.urllib3.exceptions.InsecureRequestWarning,
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning))

class TLS1HttpAdapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                   block = block, ssl_version = ssl.PROTOCOL_TLSv1)

def headers ():
  return GCU.defaultHeaders()
  

def getversion (url, root_bundle, cert, key, options = {}):
  req_data = xmlrpclib.dumps(options, methodname="GetVersion")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]
