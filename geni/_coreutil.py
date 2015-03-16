# Copyright (c) 2015  Barnstormer Softworks, Ltd.

import os
import os.path

def getDefaultDir ():
  if os.name == "posix":
    DEF_DIR = "%s/.bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
  elif os.name == "nt":
    DEF_DIR = "%s/bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
    # TODO: attrib +h somehow
  return DEF_DIR


def getDefaultContextPath ():
  ddir = getDefaultDir()
  return os.path.normpath("%s/config.json" % (ddir))
