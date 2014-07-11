# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import tempfile
import os
import os.path
import datetime

import lxml.etree as ET

from . import cmd
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

  def _build (self):
    # This really should probably be a lot more complicated/painful and be based on the "right thing"
    # for your framework - e.g. geni-ch this should contain your project, not your user name, etc.
    self._path = "%s/%s-%s-scred.xml" % (self.context.datadir, self.context._default_user.name, self.slicename)
    if not os.path.exists(self._path):
      self._downloadCredential()
    else:
      self._setExpires()

  def _downloadCredential (self):
    (text, cred) = cmd.getslicecred(self.context, self.slicename)
    if not cred:
      raise SliceCredError(text)
    f = open(self._path, "w+")
    f.write(cred)
    f.close()
    self._setExpires()

  def _setExpires (self):
    r = ET.parse(self._path)
    expstr = r.find("credential/expires").text
    if expstr[-1] == 'Z':
      expstr = expstr[:-1]
    self.expires = datetime.datetime.strptime(expstr, "%Y-%m-%dT%H:%M:%S")

  @property
  def path (self):
    checktime = datetime.datetime.now() + datetime.timedelta(minutes=5)
    if self.expires < checktime:
      # We expire in the next 5 minutes
      self._downloadCredential()
      if self.expires < datetime.datetime.now():
        raise SliceCredInfo.CredentialExpiredError(self.slicename, self.expires)
    return self._path


class Context(object):
  DEFAULT_DIR = os.path.expanduser("~/.bssw/geni")

  def __init__ (self):
    self._data_dir = None
    self._nick_cache_path = None
    self._default_user = None
    self._users = set()
    self.cf = None
    self.project = None
    self._usercred_path = None
    self._slicecreds = {}
    self.debug = False

  def _getSliceCred (self, sname):
    if not self._slicecreds.has_key(sname):
      scinfo = SliceCredInfo(self, sname)
      self._slicecreds[sname] = scinfo

    return self._slicecreds[sname].path

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

  @property
  def usercred_path (self):
    # TODO: Need to handle getting new usercred if cached one is expired
    # TODO: Need to invalidate usercred path if control framework is changed
    if self._usercred_path is None:
      if self._default_user:
        ucpath = "%s/%s-%s-usercred.xml" % (self.datadir, self._default_user.name, self.cf.name)
        if os.path.exists(ucpath):
          self._usercred_path = ucpath
        else:
          cfg = self.cfg_path
          cred = cmd.getusercred(cfg)

          f = open(ucpath, "w+")
          f.write(cred)
          path = f.name
          f.close()
          self._usercred_path = ucpath
      else:
        raise NoUserError()

    return self._usercred_path

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

