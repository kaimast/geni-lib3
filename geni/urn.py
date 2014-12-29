# Copyright (c) 2014 The University of Utah

import re

class URN (object):
  PREFIX = "urn"
  def __init__ (self, *args):
    if len(args) == 2:
      self._nid = args[0]
      self._nss = args[1]
    else:
      (_, self._nid, self._nss) = URN._fromStr(args[0])

  @staticmethod
  def _fromStr(s):
    # TODO Better actual validation
    return tuple(re.split(":",s,3))

  def __str__(self):
    return "%s:%s:%s" % (URN.PREFIX, self._nid, self._nss)

class GENIURN (URN):
  NID = "publicid"
  NSSPREFIX = "IDN"
  def __init__ (self, *args):
    if len(args) == 1:
      super(GENIURN,self).__init__(args[0])
      (self._authorities, self._type, self._name) = GENIURN._splitString(self._nss)
      None
    else:
      if not isinstance(args[0],(list, tuple)):
        self._authorities = [args[0]]
      else:
        self._authorities = args[0]
      self._type = args[1]
      self._name = args[2]
      super(GENIURN,self).__init__(GENIURN.NID,self._nssgen())

  def _nssgen(self):
    print "auth %s" % self._authorities
    return "%s+%s+%s+%s" % (GENIURN.NSSPREFIX, ":".join(self._authorities), self._type, self._name)

  @staticmethod
  def _splitString(s):
    # TODO actual validation
    matches = re.split("\+",s,4)
    return (re.split(":",matches[1]), matches[2], matches[3])

if __name__ == "__main__":
  urn = URN("publicid","thing")
  print urn
  urn2 = GENIURN("emulab.net","user","ricci")
  print urn2
  urn3 = URN("urn:isbn:0140186255")
  print urn3
  urn4 = GENIURN("urn:publicid:IDN+emulab.net+user+jay")
  print urn4
