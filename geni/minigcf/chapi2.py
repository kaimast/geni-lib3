# Copyright (c) 2015  Barnstormer Softworks, Ltd.

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

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"

class TLS1HttpAdapter(HTTPAdapter):
  def init_poolmanager(self, connections, maxsize, block=False):
    self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                   block = block, ssl_version = ssl.PROTOCOL_TLSv1)

def headers ():
  return GCU.defaultHeaders()
  
def _lookup (url, root_bundle, cert, key, typ, cred_strings, options):
  req_data = xmlrpclib.dumps((typ, cred_strings, options), methodname="lookup")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_key_info (url, root_bundle, cert, key, cred_strings, user_urn):
  options = {"match" : {"KEY_MEMBER" : user_urn} }
  return _lookup(url, root_bundle, cert, key, "KEY", cred_strings, options)
  

def get_credentials (url, root_bundle, cert, key, creds, target_urn):
  req_data = xmlrpclib.dumps((target_urn, creds, {}), methodname="get_credentials")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def create_slice (url, root_bundle, cert, key, cred_strings, name, proj_urn, exp = None, desc = None):
  fields = {}
  fields["SLICE_NAME"] = name
  fields["SLICE_PROJECT_URN"] = proj_urn
  if exp: fields["SLICE_EXPIRATION"] = exp.strftime(DATE_FMT)
  if desc: fields["SLICE_DESCRIPTION"] = desc

  req_data = xmlrpclib.dumps(("SLICE", cred_strings, {"fields" : fields}), methodname = "create")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_slices_for_member (url, root_bundle, cert, key, cred_strings, member_urn):
  options = {}

  req_data = xmlrpclib.dumps(("SLICE", member_urn, cred_strings, options), methodname = "lookup_for_member")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_slices_for_project (url, root_bundle, cert, key, cred_strings, project_urn):
  options = {"match" : {"SLICE_PROJECT_URN" : project_urn} }
  return _lookup(url, root_bundle, cert, key, "SLICE", cred_strings, options)


def create_project (url, root_bundle, cert, key, cred_strings, name, exp, desc = None):
  fields = {}
  fields["PROJECT_EXPIRATION"] = exp.strftime(DATE_FMT)
  fields["PROJECT_NAME"] = name
  if desc is not None:
    fields["PROJECT_DESC"] = desc

  req_data = xmlrpclib.dumps(("PROJECT", cred_strings, {"fields" : fields}), methodname = "create")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def delete_project (url, root_bundle, cert, key, cred_strings, project_urn):
  """Delete project by URN
  .. note:
    You may or may not be able to delete projects as a matter of policy for the given authority."""

  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "delete")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]

#def _update_project (url, root_bundle, cert, key, cred_strings, project_urn):
#  options = {"fields" : {}}
#  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "update")
#  s = requests.Session()
#  s.mount(url, TLS1HttpAdapter())
#  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
#  return xmlrpclib.loads(resp.content)[0][0]


def lookup_projects (url, root_bundle, cert, key, cred_strings, urn = None, uid = None, expired = None):
  options = { }
  match = { }
  if urn is not None:
    match["PROJECT_URN"] = urn
  if uid is not None:
    match["PROJECT_UID"] = uid
  if expired is not None:
    match["PROJECT_EXPIRED"] = expired

  if match:
    options["match"] = match

  return _lookup(url, root_bundle, cert, key, "PROJECT", cred_strings, options)


def lookup_projects_for_member (url, root_bundle, cert, key, cred_strings, member_urn):
  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", member_urn, cred_strings, options), methodname = "lookup_for_member")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_project_members (url, root_bundle, cert, key, cred_strings, project_urn):
  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "lookup_members")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers())
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_aggregates (url, root_bundle, cert, key, cred_strings):
  options = {"match" : {'SERVICE_TYPE': 'AGGREGATE_MANAGER'}}

  return _lookup(url, root_bundle, cert, key, "SERVICE", [], options)


