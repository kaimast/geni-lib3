# Copyright (c) 2013-2014  Barnstormer Softworks

import tempfile

class _Registry(object):
  def __init__ (self):
    self._data = {}

  def register (self, name, obj):
    self._data[name] = obj

  def get (self, name):
    return self._data[name]


class AM(object):
  def __init__ (self, name, url, api, framework):
    self.url = url
    self.name = name
    self._apistr = api
    self._api = None
    self._frameworkstr = framework
    self._framework = None

  @property
  def api (self):
    if not self._api:
      self._api = APIRegistry.get(self._apistr)
    return self._api

  @property
  def framework (self):
    if not self._framework:
      self._framework = FrameworkRegistry.get(self._frameworkstr)
    return self._framework


APIRegistry = _Registry()
FrameworkRegistry = _Registry()

class AMAPIv2(object):
  def _getDefaultArgs (self, context, url):
    return ["-c", context.cfg_path, "--usercredfile", context.usercred_path, "-a", url, "-V", "2"]

  def listresources (self, context, url, sname):
    arglist = self._getDefaultArgs(context, url)

    if slice:
      arglist.extend(["--slicecredfile", context.slicecred_paths[sname], "listresources", sname])
    else:
      arglist.append("listresources")

    text,res = oscript.call(arglist)
    if res.values()[0]["code"]["geni_code"] == 0:
      rspec = res.values()[0]["value"]
      return rspec

APIRegistry.register("amapiv2", AMAPIv2())

class Portal(object):
  def __init__ (self):
    self.name = "portal"
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
    l.append("[%s]" % (self.name)
    l.append("type = %s" % (self._type))
    l.append("authority = %s" % (self._authority))
    l.append("ch = %s" % (self._ch))
    l.append("sa = %s" % (self._sa))
    l.append("cert = %s" % (self.cert))
    l.append("key = %s" % (self.key))
    return l


class User(object):
  def __init__ (self):
    self.name = None
    self.urn = None
    self.keys = []

  def getConfig (self):
    l = []
    l.append("[%s]" % (self.name))
    l.append("urn = %s" % (self.urn))
    l.append("keys = %s" % (",".join(keys)))
    return l

  def addKey (self, path):
    self.keys.append(path)


class Context(object):
  def __init__ (self):
    self.user = None
    self.cf = None
    self.project = None
    self._usercred_path = None
    self._slicecred_paths = {}

  @property
  def usercred_path (self):
    if self._usercred_path is None:
      cfg = self.cfg_path
      cred = cmd.getusercred(cfg)

      # TODO: We probably want to store this one in a more static place that we can find across processes
      tf = tempfile.NamedTemporaryFile(delete=False)
      tf.write(cred)
      path = tf.name
      tf.close()
      self._usercred_path = path

     return self._usercred_path

  @property
  def cfg_path (self):
    l = []
    l.append("[omni]")
    if self.cf: l.append("default_cf = %s" % (cf.name))
    if self.project: l.append("project = %s" % (project))
    if self.users: l.append("users = %s" % (", ".join([u.name for u in self.users])))

    l.extend(self.cf.getConfig())
    l.extend(self.user.getConfig())

    # Make tempfile with proper args
    # TODO:  We need global tempfile accounting so we can clean up on terminate
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write("\n".join(l))
    path = tf.name
    tf.close()
    return path

  def addSliceCred (self, sname, path):
    self.slicecred_paths[sname] = path
