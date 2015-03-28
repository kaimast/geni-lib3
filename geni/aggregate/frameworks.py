# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import tempfile
import subprocess
import os.path

from .core import FrameworkRegistry


class Framework(object):
  class KeyPathError(Exception):
    def __init__ (self, path):
      self.path = path
    def __str__ (self):
      return "Path %s does not contain a key" % (self.path)

  def __init__ (self, name = None):
    self.name = name
    self._type = None
    self._authority = None
    self._ch = None
    self._sa = None
    self._cert = None
    self._key = None

  @property
  def key (self):
    return self._key

  @key.setter
  def key (self, val):
    # TODO:  We need global tempfile accounting so we can clean up on terminate
    if not os.path.exists(val):
      raise Framework.KeyPathError(val)
    tf = tempfile.NamedTemporaryFile(delete=False)
    path = tf.name
    tf.close()
    if os.name == "nt":
      nullf = open("NUL")
      binp = os.path.normpath("C:/OpenSSL-Win32/bin/openssl")
      ret = subprocess.call("%s rsa -in \"%s\" -out \"%s\"" % (binp, val, path), stdout=nullf, stderr=nullf, shell=True)
      self._key = path
    else:
      nullf = open("/dev/null")
      # We really don't want shell=True here, but there are pty problems with openssl otherwise
      ret = subprocess.call("/usr/bin/openssl rsa -in %s -out %s" % (val, path), stdout=nullf, stderr=nullf, shell=True)
      # TODO: Test the size afterwards to make sure the password was right, or parse stderr?
      self._key = path

  @property
  def cert (self):
    return self._cert

  @cert.setter
  def cert (self, val):
    self._cert = val

  def createslice (self, context, name):
    from ..gcf import oscript
    args = ["--warn", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "-f", self.name, "--usercredfile", context.usercred_path, "createslice"]
    args.append(name)
    (txt, res) = oscript.call(args)
    return res

  def _update (self, context):
    pass


class ProtoGENI(Framework):
  def __init__ (self, name = "pg"):
    super(ProtoGENI, self).__init__(name)
    self._type = "pgch"


class Emulab(ProtoGENI):
  def __init__ (self):
    super(Emulab, self).__init__("emulab")
    self._type = "pgch"
    self._ch = "https://www.emulab.net:443/protogeni/xmlrpc/ch"
    self._ca = "https://www.emulab.net:443/protogeni/xmlrpc/sa"


class CHAPI(Framework):
  def __init__ (self, name = "chapi"):
    super(CHAPI, self).__init__(name)
    self._type = "chapi"

  def listProjectMembers (self, context, project):
    from ..gcf import oscript
    args = ["--warn", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "-f", self.name, "--usercredfile", context.usercred_path, "listprojectmembers"]
    args.append(project)
    (txt, res) = oscript.call(args)
    return res

  def listprojects (self, context, username = None):
    from ..gcf import oscript
    args = ["--warn", "--AggNickCacheName", context.nickCache, "-c", context.cfg_path, "-f", self.name, "--usercredfile", context.usercred_path, "listprojects"]
    if username:
      args.append(username)
    (txt, res) = oscript.call(args)
    return res


class Portal(CHAPI):
  def __init__ (self):
    super(Portal, self).__init__("portal")
    self._authority = "ch.geni.net"
    self._ch = "https://ch.geni.net:8444/CH"
    self._ma = "https://ch.geni.net:443/MA"
    self._sa = "https://ch.geni.net:443/SA"

  def getConfig (self):
    l = []
    l.append("[%s]" % (self.name))
    l.append("type = %s" % (self._type))
    l.append("authority = %s" % (self._authority))
    l.append("ch = %s" % (self._ch))
    l.append("sa = %s" % (self._sa))
    l.append("ma = %s" % (self._ma))
    l.append("cert = %s" % (self.cert))
    l.append("key = %s" % (self.key))
    return l


FrameworkRegistry.register("portal", Portal)
FrameworkRegistry.register("pg", ProtoGENI)
