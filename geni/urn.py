# Copyright (c) 2014 The University of Utah

"""Simple library for manipulating URNs, particularly those used for GENI
objects"""

from __future__ import absolute_import

from geni.aggregate.core import AM
import re

class Base (object):
  """Base class representing *any* URN"""
  PREFIX = "urn"
  
  def __init__ (self, *args):
    """URNs can be initialized in one of two ways:
    1) Passing a single string in URN format (urn:NID:NSS)
    2) Passing two strings, the NID and the NSS"""
    if len(args) == 1:
      (_, self._nid, self._nss) = Base._fromStr(args[0])
    elif len(args) == 2:
      self._nid = args[0]
      self._nss = args[1]
    else:
      # TODO thrown an exception
      None

  @staticmethod
  def _fromStr(s):
    # TODO Better actual validation
    return tuple(re.split(":",s,3))

  def __str__(self):
    return "%s:%s:%s" % (Base.PREFIX, self._nid, self._nss)

class GENI (Base):
  """Class representing the URNs used by GENI, which use the publicid NID and
  IDN (domain name) scheme"""
  
  NID = "publicid"
  NSSPREFIX = "IDN"

  # Taken from the list at http://www.protogeni.net/wiki/URNs
  TYPE_AUTHORITY = "authority"
  TYPE_IMAGE     = "image"
  TYPE_INTERFACE = "interface"
  TYPE_LINK      = "link"
  TYPE_NODE      = "node"
  TYPE_SLICE     = "slice"
  TYPE_SLIVER    = "sliver"
  TYPE_USER      = "user"

  def __init__ (self, *args):
    """There are four forms of this constructor:
    1) Pass a single string in GENI URN format (urn:publicid:IDN+auth+type+name)
    2) Pass three arguments: the authority (single string), the type (see the
       TYPE_ variables above), the object name
    3) Pass three arguments: as #2, but each subauthoirty becomes its own entry
       in the list
    4) Pass three arguments: as #2, but the authority is a
       geni.aggregate.core.AM object"""
    if len(args) == 1:
      # Superclass constructor parses and sets self._nss, which we then split
      # into its constituent GENI parts
      super(GENI,self).__init__(args[0])
      self._authorities, self._type, self._name = GENI._splitNSS(self._nss)
    elif len(args) == 3:
      if isinstance(args[0],str):
        self._authorities = [args[0]]
      elif isinstance(args[0], AM):
        # TODO This might be temporary until we have AMs storing URN objects
        self._authorities = GENI(args[0].component_manager_id).authorities
      else:
        self._authorities = args[0]
      self._type = args[1]
      self._name = args[2]
      # In this form we have to reconstruct the NSS
      super(GENI,self).__init__(GENI.NID,self._makeNSS())
    else:
      # TODO throw exception
      None

  @property
  def authorities(self):
    """Returns a list containing at least one authority string (the top level
    authority) and possibly additional subauthorities"""
    return self._authorities
  
  @property
  def authority(self):
    """Return a single string that captures the entire authority/subauthority
    chain"""
    return ":".join(self._authorities)

  def _makeNSS(self):
    return "%s+%s+%s+%s" % (GENI.NSSPREFIX, self.authority, self._type,
                            self._name)

  @staticmethod
  def _splitNSS(s):
    # TODO actual validation
    matches = re.split("\+",s,4)
    return (GENI._splitAuthorities(matches[1]), matches[2], matches[3])

  @staticmethod
  def _splitAuthorities(s):
    # TODO actual validation
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
  import sys
  
  errors = 0
  
  def check_urn (urn, value):
    global errors
    if str(urn) == value:
      sys.stdout.write("PASS")
    else:
      sys.stdout.write("FAIL")
      errors = errors + 1

    sys.stdout.write(" %s / %s\n" % (urn,value))

  check_urn(Base("isbn","0553575384"),"urn:isbn:0553575384")
  check_urn(GENI("emulab.net","user","ricci"),
            "urn:publicid:IDN+emulab.net+user+ricci")
  check_urn(Base("urn:isbn:0140186255"),"urn:isbn:0140186255")
  check_urn(GENI("urn:publicid:IDN+emulab.net+user+jay"),
            "urn:publicid:IDN+emulab.net+user+jay")
  check_urn(GENI(IG.Kentucky,"user","hussam"),
            "urn:publicid:IDN+lan.sdn.uky.edu+user+hussam")
  check_urn(Image(IG.UtahDDC,"UBUNTU64-STD"),
            "urn:publicid:IDN+utahddc.geniracks.net+image+UBUNTU64-STD")
  check_urn(User(IG.Clemson,"kwang"),
            "urn:publicid:IDN+instageni.clemson.edu+user+kwang")

  sys.exit(errors)
