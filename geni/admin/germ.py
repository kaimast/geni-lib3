# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import requests.auth

import requests.packages.urllib3
import requests.packages.urllib3.exceptions
requests.packages.urllib3.disable_warnings((requests.packages.urllib3.exceptions.InsecureRequestWarning,
                                            requests.packages.urllib3.exceptions.InsecurePlatformWarning))

class Connection(object):
  def __init__ (self):
    self.user = "germadmin"
    self.password = None
    self.host = "localhost"
    self.port = 3626

  @property
  def rkwargs (self):
    d = {"headers" : self.headers,
         "auth" : self.auth,
         "verify" : False}
    return d

  @property
  def headers (self):
    return {"Content-Type" : "application/json"}

  @property
  def auth (self):
    return requests.auth.HTTPBasicAuth(self.user, self.password)

