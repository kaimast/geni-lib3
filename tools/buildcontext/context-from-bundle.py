#!/usr/bin/env python
# Copyright (c) 2015  Barnstormer Softworks, Ltd.

import zipfile
import sys
import os
import os.path
import argparse
import json

def parse_args ():
  parser = argparse.ArgumentParser()
  parser.add_argument("--pubkey", dest="pubkey_path", help="Path to public key file", default = None)
  parser.add_argument("--bundle", dest="bundle_path", help="Path to omni.bundle", default="omni.bundle")
  return parser.parse_args()

def build_context (opts):
  HOME = os.path.expanduser("~")

  # Create the .bssw directories if they don't exist
  if os.name == "posix":
    DEF_DIR = "%s/.bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
  elif os.name == "nt":
    DEF_DIR = "%s/bssw/geni/" % (HOME)
    if not os.path.exists(DEF_DIR):
      os.makedirs(DEF_DIR, 0775)
    # TODO: attrib +h somehow

  zf = zipfile.ZipFile(opts.bundle_path)

  if ("ssh/public/id_geni_ssh_rsa.pub" not in zf.namelist()) and (opts.pubkey_path is None):
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
  pkpath = opts.pubkey_path
  if not pkpath:
    if "ssh/private/id_geni_ssh_rsa" in zf.namelist():
      if not os.path.exists("%s/.ssh/id_geni_ssh_rsa" % (HOME)):
        with open("%s/.ssh/id_geni_ssh_rsa" % (HOME), "w+") as tf:
          tf.write(zf.open("ssh/private/id_geni_ssh_rsa").read())
    
    pkpath = "%s/.ssh/id_geni_ssh_rsa.pub" % (HOME)
    if not os.path.exists(pkpath):
        with open(pkpath, "w+") as tf:
          tf.write(zf.open("ssh/public/id_geni_ssh_rsa.pub").read())

  # We write the pem into 'private' space
  zf.extract("geni_cert.pem", DEF_DIR)

  cdata = {}
  cdata["cert-path"] = "%s/geni_cert.pem" % (DEF_DIR)
  cdata["key-path"] = "%s/geni_cert.pem" % (DEF_DIR)
  cdata["user-name"] = uname
  cdata["user-urn"] = urn
  cdata["user-pubkeypath"] = pkpath
  cdata["project"] = project
  json.dump(cdata, open("%s/context.json", "w+"))


if __name__ == '__main__':
  opts = parse_args()
  build_context(opts)
