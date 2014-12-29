# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

from geni.aggregate.core import AM

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
      self._authorities, self._type, self._name = GENIURN._splitString(self._nss)
    else:
      if isinstance(args[0],str):
        self._authorities = [args[0]]
      elif isinstance(args[0], AM):
        # TODO This might be temporary until we have AMs storing URN objects
        self._authorities = GENIURN(args[0].component_manager_id).authorities()
      else:
        self._authorities = args[0]
      self._type = args[1]
      self._name = args[2]
      super(GENIURN,self).__init__(GENIURN.NID,self._nssgen())

  def authorities(self):
    return self._authorities

  def _nssgen(self):
    return "%s+%s+%s+%s" % (GENIURN.NSSPREFIX, ":".join(self._authorities), self._type, self._name)

  @staticmethod
  def _splitString(s):
    # TODO actual validation
    matches = re.split("\+",s,4)
    return (GENIURN._splitAuthorities(matches[1]), matches[2], matches[3])

  @staticmethod
  def _splitAuthorities(s):
    return re.split(":",s)

if __name__ == "__main__":
  import geni.aggregate.instageni as IG

  # Lame unit tests
  urn = URN("publicid","thing")
  print urn
  urn2 = GENIURN("emulab.net","user","ricci")
  print urn2
  urn3 = URN("urn:isbn:0140186255")
  print urn3
  urn4 = GENIURN("urn:publicid:IDN+emulab.net+user+jay")
  print urn4
  urn5 = GENIURN(IG.Kentucky,"user","ricci")
  print urn5
