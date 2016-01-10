 # Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

class User(object):
  def __init__ (self):
    self.name = None
    self.urn = None
    self._keys = []

  def addKey (self, path):
    self._keys.append(path)


