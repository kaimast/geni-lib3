# Copyright (c) 2015  Barnstormer Softworks, Ltd.

import os
import os.path

WIN32_ATTR_HIDDEN = 0x02

def getDefaultDir ():
  HOME = os.path.expanduser("~")

  if os.name == "posix":
    DEF_DIR = "%s/.bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
  elif os.name == "nt":
    DEF_DIR = "%s/bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
      import ctypes
      BSSW = "%s/bssw" % (HOME)
      if not (ctypes.windll.kernel32.SetFileAttributesW(unicode(BSSW), WIN32_ATTR_HIDDEN)):
        raise ctypes.WinError()

  return DEF_DIR


def getDefaultContextPath ():
  ddir = getDefaultDir()
  return os.path.normpath("%s/context.json" % (ddir))
