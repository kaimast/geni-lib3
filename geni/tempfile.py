# Copyright (c) 2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import tempfile
import shutil

class _TempfileManager(object):
  def __init__ (self):
    self.path = tempfile.mkdtemp()

  def __del__ (self):
    shutil.rmtree(self.path, ignore_errors = True)

  def makeFile (self):
    (handle, path) = tempfile.mkstemp(dir = self.path)   
    return (handle, path)

TFM = _TempfileManager()

makeFile = TFM.makeFile
