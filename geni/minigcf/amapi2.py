# Copyright (c) 2015-2016  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning,
                                            requests.packages.urllib3.exceptions.SNIMissingWarning))

from .. import _coreutil as GCU
from . import config

class TLS1HttpAdapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                   block = block, ssl_version = ssl.PROTOCOL_TLSv1)

def headers ():
  return GCU.defaultHeaders()


def getversion (url, root_bundle, cert, key, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((options,), methodname="GetVersion")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  return xmlrpclib.loads(resp.content)[0][0]

def listresources (url, root_bundle, cert, key, cred_strings, options = None, sliceurn = None):
  if not options: options = {}
  opts = {"geni_rspec_version" : {"version" : "3", "type" : "GENI"},
          "geni_available" : False,
          "geni_compressed" : False}

  if sliceurn:
    opts["geni_slice_urn"] = sliceurn

  # Allow all options to be overridden by the caller
  opts.update(options)

  req_data = xmlrpclib.dumps((cred_strings, opts), methodname="ListResources")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  return xmlrpclib.loads(resp.content)[0][0]

def deletesliver (url, root_bundle, cert, key, creds, slice_urn, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, options), methodname="DeleteSliver")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]

def sliverstatus (url, root_bundle, cert, key, creds, slice_urn, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, options), methodname="SliverStatus")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]

def renewsliver (url, root_bundle, cert, key, creds, slice_urn, date, options = None):
  FMT = "%Y-%m-%dT%H:%M:%S+00:00"
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, date.strftime(FMT), options), methodname="RenewSliver")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert, key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]

def listimages (url, root_bundle, cert, key, cred_strings, owner_urn, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((owner_urn, cred_strings, options), methodname="ListImages")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  return xmlrpclib.loads(resp.content)[0][0]

def createsliver (url, root_bundle, cert, key, creds, slice_urn, rspec, users, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps((slice_urn, creds, rspec, users, options), methodname="CreateSliver")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  return xmlrpclib.loads(resp.content)[0][0]

