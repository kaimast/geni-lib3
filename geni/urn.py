# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

from geni.aggregate.core import AM
import re

class Base (object):
  PREFIX = "urn"
  def __init__ (self, *args):
    if len(args) == 2:
      self._nid = args[0]
      self._nss = args[1]
    else:
      (_, self._nid, self._nss) = Base._fromStr(args[0])

  @staticmethod
  def _fromStr(s):
    # TODO Better actual validation
    return tuple(re.split(":",s,3))

  def __str__(self):
    return "%s:%s:%s" % (Base.PREFIX, self._nid, self._nss)

class GENI (Base):
  NID = "publicid"
  NSSPREFIX = "IDN"

  # From the list at http://www.protogeni.net/wiki/URNs
  TYPE_AUTHORITY = "authority"
  TYPE_IMAGE     = "image"
  TYPE_INTERFACE = "interface"
  TYPE_LINK      = "link"
  TYPE_NODE      = "node"
  TYPE_SLICE     = "slice"
  TYPE_SLIVER    = "sliver"
  TYPE_USER      = "user"

  def __init__ (self, *args):
    if len(args) == 1:
      super(GENI,self).__init__(args[0])
      self._authorities, self._type, self._name = GENI._splitString(self._nss)
    else:
      if isinstance(args[0],str):
        self._authorities = [args[0]]
      elif isinstance(args[0], AM):
        # TODO This might be temporary until we have AMs storing URN objects
        self._authorities = GENI(args[0].component_manager_id).authorities()
      else:
        self._authorities = args[0]
      self._type = args[1]
      self._name = args[2]
      super(GENI,self).__init__(GENI.NID,self._nssgen())

  def authorities(self):
    return self._authorities

  def _nssgen(self):
    return "%s+%s+%s+%s" % (GENI.NSSPREFIX, ":".join(self._authorities), self._type, self._name)

  @staticmethod
  def _splitString(s):
    # TODO actual validation
    matches = re.split("\+",s,4)
    return (GENI._splitAuthorities(matches[1]), matches[2], matches[3])

  @staticmethod
  def _splitAuthorities(s):
    return re.split(":",s)

class Authority (GENI):
  def __init__ (self, authorities, name):
    super(Authority,self).__init(authorities, GENI.TYPE_AUTHORITY, name)

class Interface (GENI):
  def __init__ (self, authorities, name):
    super(Interface,self).__init(authorities, GENI.TYPE_INTERFACE, name)

class Image (GENI):
  def __init__ (self, authorities, name):
    super(Image,self).__init__(authorities, GENI.TYPE_IMAGE, name)

class Link (GENI):
  def __init__ (self, authorities, name):
    super(Link,self).__init(authorities, GENI.TYPE_LINK, name)

class Node (GENI):
  def __init__ (self, authorities, name):
    super(Node,self).__init(authorities, GENI.TYPE_NODE, name)

class Slice (GENI):
  def __init__ (self, authorities, name):
    super(Slice,self).__init(authorities, GENI.TYPE_SLICE, name)

class Sliver (GENI):
  def __init__ (self, authorities, name):
    super(Sliver,self).__init(authorities, GENI.TYPE_SLIVER, name)

class User (GENI):
  def __init__ (self, authorities, name):
    super(User,self).__init__(authorities, GENI.TYPE_USER, name)

if __name__ == "__main__":
  # Lame unit tests
  import geni.aggregate.instageni as IG

  urn = Base("publicid","thing")
  print urn
  urn2 = GENI("emulab.net","user","ricci")
  print urn2
  urn3 = Base("urn:isbn:0140186255")
  print urn3
  urn4 = GENI("urn:publicid:IDN+emulab.net+user+jay")
  print urn4
  urn5 = GENI(IG.Kentucky,"user","ricci")
  print urn5
  urn6 = Image(IG.UtahDDC,"UBUNTU64-STD")
  print urn6
  urn6 = User(IG.Clemson,"kwang")
  print urn6
