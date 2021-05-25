# Copyright (c) 2015-2018    Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Streamlined implementation of xmlrpc calls to AM API v3-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

from six.moves import xmlrpc_client as xmlrpclib

from .util import _rpcpost

# pylint: disable=unsubscriptable-object
def getversion(url, root_bundle, cert, key, options = {}):
    req_data = xmlrpclib.dumps(options, methodname="GetVersion")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def poa(url, root_bundle, cert, key, creds, urns, action, options = {}):
    if not isinstance(urns, list):
        urns = [urns]

    cred_list = []
    for cred in creds:
        cred_list.append({"geni_value" : open(cred.path, "rb").read(),
            "geni_type" : cred.type, "geni_version" : cred.version})

    req_data = xmlrpclib.dumps((urns, cred_list, action, options),
                                 methodname="PerformOperationalAction")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def paa (url, root_bundle, cert, key, action, options = {}):
    req_data = xmlrpclib.dumps((action, options), methodname="PerformAggregateAction")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def allocate(url, root_bundle, cert, key, creds, slice_urn, rspec, options = {}):
    cred_list = []
    for cred in creds:
        cred_list.append({"geni_value" : open(cred.path, "rb").read(),
            "geni_type" : cred.type, "geni_version" : cred.version})

    req_data = xmlrpclib.dumps((slice_urn, cred_list, rspec, options), methodname="Allocate")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def provision(url, root_bundle, cert, key, creds, urns, options = {}):
    if not isinstance(urns, list):
        urns = [urns]

    cred_list = []
    for cred in creds:
        cred_list.append({"geni_value" : open(cred.path, "rb").read(),
            "geni_type" : cred.type, "geni_version" : cred.version})

    req_data = xmlrpclib.dumps((urns, cred_list, options), methodname="Provision")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def delete(url, root_bundle, cert, key, creds, urns, options = {}):
    if not isinstance(urns, list):
        urns = [urns]

    cred_list = []
    for cred in creds:
        cred_list.append({"geni_value" : open(cred.path, "rb").read(),
            "geni_type" : cred.type, "geni_version" : cred.version})

    req_data = xmlrpclib.dumps((urns, cred_list, options), methodname="Delete")
    return _rpcpost(url, req_data, (cert, key), root_bundle)
