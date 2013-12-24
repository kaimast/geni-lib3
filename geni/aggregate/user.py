 # Copyright (c) 2014  Barnstormer Softworks, Ltd.

class User(object):
  def __init__ (self):
    self.name = None
    self.urn = None
    self._keys = []

  def getConfig (self):
    l = []
    l.append("[%s]" % (self.name))
    l.append("urn = %s" % (self.urn))
    l.append("keys = %s" % (",".join(self._keys)))
    return l

  def addKey (self, path):
    self._keys.append(path)


