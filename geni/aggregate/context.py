# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import tempfile
import os
import os.path
import datetime

import lxml.etree as ET

from ..exceptions import NoUserError, SliceCredError

class SlicecredProxy(object):
  def __init__ (self, context):
    self._context = context

  def __getitem__ (self, name):
    return self._context._getSliceCred(name)

  def iteritems (self):
    return self._context._slicecred_paths.iteritems()

  def iterkeys (self):
    return self._context._slicecred_paths.iterkeys()

  def __iter__ (self):
    for x in self._context._slicecred_paths:
      yield x

class SliceCredInfo(object):
  class CredentialExpiredError(Exception):
    def __init__ (self, name, expires):
      self.expires = expires
      self.sname = name
    def __str__ (self):
      return "Credential for slice %s expired on %s" % (self.sname, self.expires)

  def __init__ (self, context, slicename):
    self.slicename = slicename
    self.context = context
    self._path = None
    self.expires = None
    self._build()
    self.urn = None

  def _build (self):
    # This really should probably be a lot more complicated/painful and be based on the "right thing"
    # for your framework - e.g. geni-ch this should contain your project, not your user name, etc.
    self._path = "%s/%s-%s-%s-scred.xml" % (self.context.datadir, self.context._default_user.name,
                                            self.context.project, self.slicename)
    if not os.path.exists(self._path):
      self._downloadCredential()
    else:
      self._parseInfo()

  def _downloadCredential (self):
    cred = self.context.cf.getSliceCredentials(self.context, self.slicename)

#      raise SliceCredError(text)

    f = open(self._path, "w+")
    f.write(cred)
    f.close()
    self._parseInfo()

  def _parseInfo (self):
    r = ET.parse(self._path)

    # Expiration
    expstr = r.find("credential/expires").text
    if expstr[-1] == 'Z':
      expstr = expstr[:-1]
    self.expires = datetime.datetime.strptime(expstr, "%Y-%m-%dT%H:%M:%S")

    # URN
    self.urn = r.find("credential/target_urn").text

  @property
  def path (self):
    checktime = datetime.datetime.now() + datetime.timedelta(days=6)
    if self.expires < checktime:
      # We expire in the next 6 days
      # TODO: Log something
      self._downloadCredential()
      if self.expires < datetime.datetime.now():
        raise SliceCredInfo.CredentialExpiredError(self.slicename, self.expires)
    return self._path


class Context(object):
  DEFAULT_DIR = os.path.expanduser("~/.bssw/geni")

  class UserCredExpiredError(Exception):
    def __init__ (self, expires):
      self.expires = expires
    def __str__ (self):
      return "User Credential expired on %s" % (self.expires)

  def __init__ (self):
    self._data_dir = None
    self._nick_cache_path = None
    self._default_user = None
    self._users = set()
    self._cf = None
    self._project = None
    self._project_urn = None
    self._usercred_info = None  # (path, expires, urn)
    self._slicecreds = {}
    self.debug = False

  def _getSliceCred (self, sname):
    info = self.getSliceInfo(sname)
    return info.path

  def _getCredInfo(self, path):
    r = ET.parse(path)
    expstr = r.find("credential/expires").text
    if expstr[-1] == 'Z':
      expstr = expstr[:-1]
    exp = datetime.datetime.strptime(expstr, "%Y-%m-%dT%H:%M:%S")
    urn = r.find("credential/target_urn").text

    return (exp, urn)

  @property
  def userurn (self):
    return self._ucred_info[2]

  @property
  def project (self):
    return self._project

  @project.setter
  def project (self, val):
    self._project = val
    self._project_urn = None

  @property
  def project_urn (self):
    if self._project_urn is None:
      pass
    return self._project_urn

  @property
  def cf (self):
    return self._cf

  @cf.setter
  def cf (self, value):
    # TODO: Calllback into framework here?  Maybe addressed with ISSUE-2
    # Maybe declare writing the _cf more than once as Unreasonable(tm)?
    self._cf = value
    self._usercred_info = None

  @property
  def nickCache (self):
    if self._nick_cache_path is None:
      cachepath = os.path.normpath("%s/nickcache.json" % (self.datadir))
      self._nick_cache_path = cachepath
    return self._nick_cache_path

  @property
  def datadir (self):
    if self._data_dir is None:
      if not os.path.exists(Context.DEFAULT_DIR):
        os.makedirs(Context.DEFAULT_DIR)
      self._data_dir = Context.DEFAULT_DIR
    return self._data_dir

  @datadir.setter
  def datadir (self, val):
    nval = os.path.expanduser(os.path.normpath(val))
    if not os.path.exists(nval):
      os.makedirs(nval)
    self._data_dir = nval

### TODO: User credentials need to belong to Users, or fix up this profile nonsense
  @property
  def _ucred_info (self):
    if self._usercred_info is None:
      if self._default_user:
        ucpath = "%s/%s-%s-usercred.xml" % (self.datadir, self._default_user.name, self.cf.name)
        if not os.path.exists(ucpath):
          cfg = self.cfg_path
          cred = self.cf.getUserCredentials(self, self._default_user.urn)

          f = open(ucpath, "w+")
          f.write(cred)
          path = f.name
          f.close()

        (expires, urn) = self._getCredInfo(ucpath)
        self._usercred_info = (ucpath, expires, urn)
      else:
        raise NoUserError()
    return self._usercred_info
    
  @property
  def usercred_path (self):
    # If you only need a user cred, something that works in the next 5 minutes is fine.  If you
    # are doing something more long term then you need a slice credential anyhow, whose
    # expiration will stop you as it should not outlast the user credential (and if it does,
    # some clearinghouse has decided that is allowed).
    checktime = datetime.datetime.now() + datetime.timedelta(minutes=5)
    if self._ucred_info[1] < checktime:
      # Delete the user cred and hope you already renewed it
      try:
        os.remove(self._ucred_info[1])
        self._usercred_info = None
      except OSError, e:
        # Windows won't let us remove open files
        # TODO: A place for some debug logging
        pass

    if self._ucred_info[1] < datetime.datetime.now():
      raise Context.UserCredExpiredError(self._ucred_info[1])
    
    return self._ucred_info[0]

  @property
  def cfg_path (self):
    l = []
    l.append("[omni]")
    if self.cf: l.append("default_cf = %s" % (self.cf.name))
    if self.project: l.append("default_project = %s" % (self.project))
    if self._users: l.append("users = %s" % (", ".join([u.name for u in self._users])))
    l.append("")

    l.extend(self.cf.getConfig())
    l.append("")

    for user in self._users:
      l.extend(user.getConfig())
      l.append("")

    # Make tempfile with proper args
    # TODO:  We need global tempfile accounting so we can clean up on terminate
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write("\n".join(l))
    path = tf.name
    tf.close()
    return path

  def addSliceCred (self, sname, path):
    self.slicecred_paths[sname] = path

  def addUser (self, user, default = False):
    self._users.add(user)
    if default:
      self._default_user = user

  @property
  def slicecreds (self):
    return SlicecredProxy(self)

  def getSliceInfo (self, sname):
    if not self._slicecreds.has_key(sname):
      scinfo = SliceCredInfo(self, sname)
      self._slicecreds[sname] = scinfo
    return self._slicecreds[sname]

