# Copyright (c) 2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from .exceptions import AMError

class ProtoGENIError(AMError): pass

class VLANUnavailableError(ProtoGENIError): pass
class InsufficientBandwdithError(ProtoGENIError): pass
class InsufficientNodesError(ProtoGENIError): pass
class InsufficientMemoryError(ProtoGENIError): pass
class NoMappingError(ProtoGENIError): pass

def raiseError(res):
  amcode = res["code"]["am_code"]
  value = res["value"]
  if amcode == 24:
    raise VLANUnavailableError(value, res)
  elif amcode == 25:
    raise InsufficientBandwidthError(value, res)
  elif amcode == 26:
    raise InsufficientNodesError(value, res)
  elif amcode == 27:
    raise InsufficientMemoryError(value, res)
  elif amcode == 28:
    raise NoMappingError(value, res)
  else:
    raise ProtoGENIError(value, res)
