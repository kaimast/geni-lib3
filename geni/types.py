# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class DPID(object):
  MAX = (2 ** 64) - 1

  class OutOfRangeError(Exception):
    def __init__ (self, val):
      super(DPID.OutOfRangeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%d) out of range of valid DPIDs" % (self.val)

  class InputTypeError(Exception):
    def __init__ (self, val):
      super(DPID.InputTypeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%s) has invalid type (%s)" % (self.val, type(self.val))

  def __init__ (self, val):
    self._dpid = None

    if isinstance(val, (unicode, str)):
      val = int(val.replace(":", ""), 16)

    if isinstance(val, (int, long)):
      if val < DPID.MAX and val >= 0:
        self._dpid = val
      else:
        raise DPID.OutOfRangeError(val)
    else:
      raise DPID.InputTypeError(val)

  def __eq__ (self, other):
    return self._dpid == other._dpid # pylint: disable=W0212

  def __hash__ (self):
    return self._dpid

  def __str__ (self):
    s = self.hexstr()
    return ":".join(["%s%s" % (s[x], s[x+1]) for x in xrange(0,15,2)])

  def __repr__ (self):
    return str(self)

  def __json__ (self):
    return str(self)

  def hexstr (self):
    return "%016x" % (self._dpid)

class EthernetMAC (object):
  MAX = (2 ** 48) - 1

  class OutOfRangeError(Exception):
    def __init__ (self, val):
      super(EthernetMAC.OutOfRangeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%d) out of range of valid Ethernet Addresses" % (self.val)

  class InputTypeError(Exception):
    def __init__ (self, val):
      super(EthernetMAC.InputTypeError, self).__init__()
      self.val = val
    def __str__ (self):
      return "Input value (%s) has invalid type (%s)" % (self.val, type(self.val))

  def __init__ (self, val):
    self._mac = None

    if isinstance(val, (unicode, str)):
      val = val.replace(":", "")
      val = val.replace("-", "")
      val = int(val, 16)

    if isinstance(val, (long, int)):
      if val < EthernetMAC.MAX and val >= 0:
        self._mac = val
      else:
        raise EthernetMAC.OutOfRangeError(val)
    else:
      raise EthernetMAC.InputTypeError(val)

  def __eq__ (self, other):
    return self._mac == other._mac # pylint: disable=W0212

  def __hash__ (self):
    return self._mac

  def __str__ (self):
    s = self.hexstr()
    return ":".join(["%s%s" % (s[x], s[x+1]) for x in range(0,11,2)])

  def __json__ (self):
    return str(self)

  def __repr__ (self):
    return str(self)

  def hexstr (self):
    return "%012x" % (self._mac)
