# Copyright (c) 2013  Barnstormer Softworks, Ltd

class XMLContext(object):
  def __init__ (self, rspec, root, cur_elem = None):
    self.rspec = rspec
    self.root = root
    self.curelem = cur_elem
