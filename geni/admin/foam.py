# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import requests

from . import germ

class Connection(germ.Connection):
  def __init__ (self):
    super(Connection, self).__init__()
    self.user = "foamadmin"
