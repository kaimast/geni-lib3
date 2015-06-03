# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# Streamlined implementation of xmlrpc calls to AM API v2-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

from __future__ import absolute_import

import xmlrpclib
import ssl

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# We need to suppress warnings that assume we want a level of security we aren't actually asking for
import requests.packages.urllib3
import requests.packages.urllib3.exceptions
requests.packages.urllib3.disable_warnings((requests.packages.urllib3.exceptions.InsecureRequestWarning,
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning))

class TLS1HttpAdapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                   block = block, ssl_version = ssl.PROTOCOL_TLSv1)


def getversion (url, root_bundle, cert, key):
  req_data = xmlrpclib.dumps((), methodname="GetVersion")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle)
  return xmlrpclib.loads(resp.content)[0][0]

def listresources (url, root_bundle, cert, key, cred_strings, sliceurn = None):
  options = {"geni_rspec_version" : {"version" : 3, "type" : "GENI"},
             "geni_available" : False,
             "geni_compressed" : False}

  if sliceurn:
    options["geni_slice_urn"] = sliceurn

  req_data = xmlrpclib.dumps((cred_strings, options), methodname="ListResources")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter(root_bundle))
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle)
  return xmlrpclib.loads(resp.content)[0][0]

def sliverstatus (url, roots, cert, key, cred_strings, sliceurn):
  pass
