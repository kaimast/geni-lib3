# Copyright (c) 2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from .util import _rpcpost

def ListComponents(url, root_bundle, cert, key, cred_strings):
  req_data = xmlrpclib.dumps((cred_strings,), methodname="ListComponents")
  return _rpcpost(url, req_data, (cert,key), root_bundle)
