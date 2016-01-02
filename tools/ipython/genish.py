# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# genish as an iPython extension for use with Jupyter

import types

import graphviz
import pandas

from geni.aggregate.frameworks import KeyDecryptionError
import geni.util

######
### iPython-specific Utilities
######
def topo (manifests):
  if not isinstance(manifests, list):
    manifests = [manifests]

  dotstr = geni.util.builddot(manifests)
  return graphviz.Source(dotstr)


def loginInfo (manifests):
  df = pandas.DataFrame.from_records(geni.util._corelogininfo(manifests),
                                     columns = ["client-id", "username", "host", "port"])
  return df


util = types.ModuleType("geni_ipython_util")
setattr(util, "showtopo", topo)
setattr(util, "printlogininfo", loginInfo)

#####
### Extension loader
#####
def load_ipython_extension (ipy):
  imports = {}

  import geni.util
  import geni.rspec.pg
  import geni.rspec.vts
  import geni.rspec.igext
  import geni.rspec.egext
  import geni.rspec.igutil
  import geni.aggregate.frameworks
  import geni.aggregate.instageni
  import geni.aggregate.vts
  import geni.aggregate.exogeni
  import geni.aggregate.cloudlab
  import geni.aggregate.transit
  import pprint

  imports["util"] = util
  imports["PG"] = geni.rspec.pg
  imports["VTS"] = geni.rspec.vts
  imports["IGAM"] = geni.aggregate.instageni
  imports["VTSAM"] = geni.aggregate.vts
  imports["EGAM"] = geni.aggregate.exogeni
  imports["CLAM"] = geni.aggregate.cloudlab
  imports["TRANSITAM"] = geni.aggregate.transit
  imports["IGX"] = geni.rspec.igext
  imports["EGX"] = geni.rspec.egext
  imports["IGUtil"] = geni.rspec.igutil
  imports["PP"] = pprint.pprint
  imports["RegM"] = geni.aggregate.frameworks.MemberRegistry

  import getpass

  tries = 0
  while True:
    pw = getpass.getpass("Private Key Passphrase: ")
    tries += 1
    try:
      imports["context"] = geni.util.loadContext(key_passphrase = pw)
      break
    except KeyDecryptionError:
      if tries < 3:
        continue
      break
    except IOError:
      break

  ipy.push(imports)
