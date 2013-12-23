# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import tempfile

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
