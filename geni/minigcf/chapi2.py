# Copyright (c) 2015-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import xmlrpclib
import ssl

import requests
from requests.adapters import HTTPAdapter

from .. import _coreutil as GCU
from . import config

GCU.disableUrllibWarnings()

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"

try:
  from requests.packages.urllib3.poolmanager import PoolManager
  class TLS1HttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
      self.poolmanager = PoolManager(num_pools = connections, maxsize = maxsize,
                                     block = block, ssl_version = ssl.PROTOCOL_TLSv1)
except ImportError:
  TLS1HttpAdapter = HTTPAdapter


class SLICE_ROLE(object):
  LEAD = "LEAD"
  ADMIN = "ADMIN"
  MEMBER = "MEMBER"
  OPERATOR = "OPERATOR"
  AUDITOR = "AUDITOR"

class PROJECT_ROLE(object):
  LEAD = "LEAD"
  MEMBER = "MEMBER"


def headers ():
  return GCU.defaultHeaders()

# pylint: disable=unsubscriptable-object
def _lookup (url, root_bundle, cert, key, typ, cred_strings, options):
  req_data = xmlrpclib.dumps((typ, cred_strings, options), methodname="lookup")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]

def get_version (url, root_bundle, cert, key, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps(tuple(), methodname = "get_version")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]
  

def lookup_key_info (url, root_bundle, cert, key, cred_strings, user_urn):
  options = {"match" : {"KEY_MEMBER" : user_urn} }
  return _lookup(url, root_bundle, cert, key, "KEY", cred_strings, options)

def lookup_member_info (url, root_bundle, cert, key, cred_strings, user_urn):
  options = {"match" : {"MEMBER_URN" : user_urn} }
  return _lookup(url, root_bundle, cert, key, "MEMBER", cred_strings, options)

def create_key_info (url, root_bundle, cert, key, cred_strings, data):
  req_data = xmlrpclib.dumps(("KEY", cred_strings, {"fields" : data}), methodname="create")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def get_credentials (url, root_bundle, cert, key, creds, target_urn):
  req_data = xmlrpclib.dumps((target_urn, creds, {}), methodname="get_credentials")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def create_slice (url, root_bundle, cert, key, cred_strings, name, proj_urn, exp = None, desc = None):
  fields = {}
  fields["SLICE_NAME"] = name
  if proj_urn: fields["SLICE_PROJECT_URN"] = proj_urn
  if exp: fields["SLICE_EXPIRATION"] = exp.strftime(DATE_FMT)
  if desc: fields["SLICE_DESCRIPTION"] = desc

  req_data = xmlrpclib.dumps(("SLICE", cred_strings, {"fields" : fields}), methodname = "create")

  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def update_slice (url, root_bundle, cert, key, cred_strings, slice_urn, fields):
  req_data = xmlrpclib.dumps(("SLICE", slice_urn, cred_strings, {"fields" : fields}), methodname = "update")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_slices_for_member (url, root_bundle, cert, key, cred_strings, member_urn):
  options = {}

  req_data = xmlrpclib.dumps(("SLICE", member_urn, cred_strings, options), methodname = "lookup_for_member")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_slices_for_project (url, root_bundle, cert, key, cred_strings, project_urn):
  options = {"match" : {"SLICE_PROJECT_URN" : project_urn} }
  return _lookup(url, root_bundle, cert, key, "SLICE", cred_strings, options)


def lookup_slice_members (url, root_bundle, cert, key, cred_strings, slice_urn):
  options = {}

  req_data = xmlrpclib.dumps(("SLICE", slice_urn, cred_strings, options), methodname = "lookup_members")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def create_project (url, root_bundle, cert, key, cred_strings, name, exp, desc = None):
  fields = {}
  fields["PROJECT_EXPIRATION"] = exp.strftime(DATE_FMT)
  fields["PROJECT_NAME"] = name
  if desc is not None:
    fields["PROJECT_DESC"] = desc

  req_data = xmlrpclib.dumps(("PROJECT", cred_strings, {"fields" : fields}), methodname = "create")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def delete_project (url, root_bundle, cert, key, cred_strings, project_urn):
  """Delete project by URN
  .. note::
    You may or may not be able to delete projects as a matter of policy for the given authority."""

  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "delete")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
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
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_project_members (url, root_bundle, cert, key, cred_strings, project_urn):
  options = {}

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "lookup_members")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def lookup_aggregates (url, root_bundle, cert, key):
  options = {"match" : {'SERVICE_TYPE': 'AGGREGATE_MANAGER'}}

  return _lookup(url, root_bundle, cert, key, "SERVICE", [], options)


def modify_slice_membership (url, root_bundle, cert, key, cred_strings, slice_urn, add = None, remove = None, change = None):
  options = {}
  if add:
    to_add = []
    for urn,role in add:
      to_add.append({"SLICE_MEMBER" : urn, "SLICE_ROLE" : role})
    options["members_to_add"] = to_add
  if remove:
    options["members_to_remove"] = remove
  if change:
    to_change = []
    for urn,role in change:
      to_change.append({"SLICE_MEMBER" : urn, "SLICE_ROLE" : role})
    options["members_to_change"] = to_change

  req_data = xmlrpclib.dumps(("SLICE", slice_urn, cred_strings, options), methodname = "modify_membership")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]


def modify_project_membership (url, root_bundle, cert, key, cred_strings, project_urn, add = None, remove = None, change = None):
  options = {}
  if add:
    to_add = []
    for urn,role in add:
      to_add.append({"PROJECT_MEMBER" : urn, "PROJECT_ROLE" : role})
    options["members_to_add"] = to_add
  if remove:
    options["members_to_remove"] = remove
  if change:
    to_change = []
    for urn,role in change:
      to_change.append({"PROJECT_MEMBER" : urn, "PROJECT_ROLE" : role})
    options["members_to_change"] = to_change

  req_data = xmlrpclib.dumps(("PROJECT", project_urn, cred_strings, options), methodname = "modify_membership")
  s = requests.Session()
  s.mount(url, TLS1HttpAdapter())
  resp = s.post(url, req_data, cert=(cert,key), verify=root_bundle, headers = headers(),
                timeout = config.HTTP.TIMEOUT, allow_redirects = config.HTTP.ALLOW_REDIRECTS)
  if isinstance(config.HTTP.LOG_RAW_RESPONSES, tuple):
    config.HTTP.LOG_RAW_RESPONSES[0].log(config.HTTP.LOG_RAW_RESPONSES[1], resp.content)
  return xmlrpclib.loads(resp.content)[0][0]

