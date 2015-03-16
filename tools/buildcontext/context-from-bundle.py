#!/usr/bin/env python
# Copyright (c) 2015  Barnstormer Softworks, Ltd.

import zipfile
import sys
import os
import os.path

TEMPLATE = """
from geni.aggregate import FrameworkRegistry
from geni.aggregate.context import Context
from geni.aggregate.user import User

def build ():
  portal = FrameworkRegistry.get("portal")()
  portal.cert = "%(certpath)s"
  portal.key = "%(keypath)s"

  user = User()
  user.name = "%(username)s"
  user.urn = "%(userurn)s"
  user.addKey("%(pubkeypath)s")

  context = Context()
  context.addUser(user, default = True)
  context.cf = portal
  context.project = "%(project)s"

  return context
"""


def parse_args ():
  return None

def build_context (opts):
  HOME = os.path.expanduser("~")

  # Create the .bssw directories if they don't exist
  if os.name = "posix":
    DEF_DIR = "%s/.bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
  elif os.name = "nt":
    DEF_DIR = "%s/bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
    # TODO: attrib +h somehow

  zf = zipfile.ZipFile(opts.bundle_path)

  if "ssh/public/id_geni_ssh_rsa.pub" not in zf.namelist() and
    opts.pubkey_path is None:
    print "Your bundle does not contain an SSH public key.  You must specify one using a command line argument."
    sys.exit()
    

  # Get URN/Project/username from omni_config
  urn = None
  project = None

  oc = zf.open("omni_config")
  for l in oc.readlines():
    if l.startswith("urn"):
      urn = l.split("=")[1].strip()
    elif l.startswith("default_project"):
      project = l.split("=")[1].strip()
  
  uname = urn.rsplit("+")[-1]

  # Create .ssh if it doesn't exist
  try:
    os.makedirs("%s/.ssh" % (HOME), 0775)
  except OSError, e:
    pass

  # If a pubkey wasn't supplied on the command line, we may need to install both keys from the bundle
  if not opts.pubkey_path:
    if "ssh/private/id_geni_ssh_rsa" in zf.namelist():
      if not os.path.exists("%s/.ssh/id_geni_ssh_rsa" % (HOME)):
        zf.extract("ssh/private/id_geni_ssh_rsa", "%s/.ssh/" % (HOME))
    
    if not os.path.exists("%s/.ssh/id_geni_ssh_rsa.pub" % (HOME)):
      zf.extract("ssh/public/id_geni_ssh_rsa.pub", "%s/.ssh/" % (HOME))

  # We write the pem into 'private' space
  zf.extract("geni_cert.pem", DEF_DIR)



if __name__ == '__main__':
  opts = parse_args()
  build_context(opts)
