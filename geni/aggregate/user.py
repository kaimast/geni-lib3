 # Copyright (c) 2014  Barnstormer Softworks, Ltd.

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


