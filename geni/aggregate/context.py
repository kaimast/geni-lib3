# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import tempfile
from . import cmd

class Context(object):
  def __init__ (self):
    self._default_user = None
    self._users = set()
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
    if self.cf: l.append("default_cf = %s" % (self.cf.name))
    if self.project: l.append("project = %s" % (self.project))
    if self._users: l.append("users = %s" % (", ".join([u.name for u in self._users])))

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
