# Copyright (c) 2015  Barnstormer Softworks, Ltd.

"""
Tempfile Manager to enable secure creation of temporary files, and deletion on process exit.

The module-level `makeFile` method uses a pre-existing singleton manager for the entire process,
while individual `TempfileManager` instances can be created to serve different user needs and scopes.
"""

from __future__ import absolute_import

import tempfile
import shutil

class TempfileManager(object):
  """Global tempfile manager for the current process that guarantees deletion when the process ends."""

  def __init__ (self):
    self.path = tempfile.mkdtemp()

  def __del__ (self):
    shutil.rmtree(self.path, ignore_errors = True)

  def makeFile (self):
    """Create a temporary file.  The open file handle and full path are returned.
       .. note:
         You may delete this file at any time, otherwise it will be deleted when the process exits."""
    (handle, path) = tempfile.mkstemp(dir = self.path)
    return (handle, path)

TFM = TempfileManager()

makeFile = TFM.makeFile
