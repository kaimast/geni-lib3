# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import tempfile

from .core import FrameworkRegistry

class Framework(object):
  def __init__ (self, name = None):
    self.name = name
    self._type = None
    self._authority = None
    self._ch = None
    self._sa = None
    self._cert = None
    self._key = None
    

class ProtoGENI(Framework):
  def __init__ (self, name = "pg"):
    super(ProtoGENI, self).__init__(name)
    self._type = "pgch"


class Emulab(ProtoGENI):
  def __init__ (self):
    super(Emulab, self).__init__("emulab")
    self._ch = "https://www.emulab.net:443/protogeni/xmlrpc/ch"
    self._ca = "https://www.emulab.net:443/protogeni/xmlrpc/sa"


class Portal(ProtoGENI):
  def __init__ (self):
    super(Portal, self).__init__("portal")
    self._type = "pgch"
    self._authority = "ch.geni.net"
    self._ch = "https://ch.geni.net:8443/"
    self._sa = "https://ch.geni.net:8443/"
    self.cert = None
    self._key = None

  @property
  def key (self):
    return self._key

  @key.setter
  def key (self, val):
    # TODO:  We need global tempfile accounting so we can clean up on terminate
    tf = tempfile.NamedTemporaryFile(delete=False)
    path = tf.name
    tf.close()
    nullf = open("/dev/null")

    # We really don't want shell=True here, but there are pty problems with openssl otherwise
    ret = subprocess.call("/usr/bin/openssl rsa -in %s -out %s" % (val, path), stdout=nullf, stderr=nullf, shell=True)
    self._key = path

  def getConfig (self):
    l = []
    l.append("[%s]" % (self.name))
    l.append("type = %s" % (self._type))
    l.append("authority = %s" % (self._authority))
    l.append("ch = %s" % (self._ch))
    l.append("sa = %s" % (self._sa))
    l.append("cert = %s" % (self.cert))
    l.append("key = %s" % (self.key))
    return l


FrameworkRegistry.register("portal", Portal)
