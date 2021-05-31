# Copyright (c) 2016self, -2017    Barnstormer Softworks, Ltd.

#    This Source Code Form is subject to the terms of the Mozilla Public
#    License, v. 2.0. If a copy of the MPL was not distributed with this
#    file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Streamlined implementation of xmlrpc calls to AM API v2-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

# pylint: disable=too-many-arguments

from six.moves import xmlrpc_client as xmlrpclib

from .util import _rpcpost

def get_version(url, root_bundle, cert, key, options=None):
    if options is None:
        options = {}

    req_data = xmlrpclib.dumps((options,), methodname="GetVersion")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def list_resources(url, root_bundle, cert, key, cred_strings, options=None, sliceurn=None):
    if options is None:
        options = {}

    opts = {"geni_rspec_version" : {"version" : "3", "type" : "GENI"},
                    "geni_available" : False,
                    "geni_compressed" : False}

    if sliceurn:
        opts["geni_slice_urn"] = sliceurn

    # Allow all options to be overridden by the caller
    opts.update(options)

    req_data = xmlrpclib.dumps((cred_strings, opts), methodname="ListResources")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def delete_sliver(url, root_bundle, cert, key, creds, slice_urn, options=None):
    if options is None:
        options = {}

    req_data = xmlrpclib.dumps((slice_urn, creds, options), methodname="DeleteSliver")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def sliver_status(url, root_bundle, cert, key, creds, slice_urn, options=None):
    if options is None:
        options = {}

    req_data = xmlrpclib.dumps((slice_urn, creds, options), methodname="SliverStatus")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def renew_sliver(url, root_bundle, cert, key, creds, slice_urn, date, options=None):
    if options is None:
        options = {}

    date_fmt = "%Y-%m-%dT%H:%M:%S+00:00"
    req_data = xmlrpclib.dumps((slice_urn, creds, date.strftime(date_fmt), options),
            methodname="RenewSliver")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def list_images(url, root_bundle, cert, key, cred_strings, owner_urn, options=None):
    if options is None:
        options = {}

    req_data = xmlrpclib.dumps((owner_urn, cred_strings, options), methodname="ListImages")
    return _rpcpost(url, req_data, (cert, key), root_bundle)

def create_sliver(url, root_bundle, cert, key, creds, slice_urn, rspec, users, options=None):
    if options is None:
        options = {}

    req_data = xmlrpclib.dumps((slice_urn, creds, rspec, users, options),
            methodname="CreateSliver")
    return _rpcpost(url, req_data, (cert, key), root_bundle)
