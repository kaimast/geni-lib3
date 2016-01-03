# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# genish as an iPython extension for use with Jupyter

import types

import graphviz
import pandas

from geni.aggregate.frameworks import KeyDecryptionError
from geni.aggregate.vts import VTS
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
  linfo = geni.util._corelogininfo(manifests)
  df = pandas.DataFrame.from_records([x[1:] for x in linfo],
                                     index = [x[0] for x in linfo],
                                     columns = ["username", "host", "port"])
  return df


util = types.ModuleType("geni_ipython_util")
setattr(util, "showtopo", topo)
setattr(util, "printlogininfo", loginInfo)

#####
### Core geni-lib monkeypatches
#####

def dumpMACs (self, context, sname, datapaths):
  if not isinstance(datapaths, list):
    datapaths = [datapaths]

  res = self._dumpMACs(context, sname, datapaths)
  init = False
  data = []
  idx_list = []
  for k,v in res.iteritems():
    if not init:
      cols = v[0]
      init = True
    
    if len(v) > 1:
      idx_list.append(k)
    for row in v[2:]:
      idx_list.append('')
    data.extend(v[1:])

  return pandas.DataFrame.from_records(data, index = idx_list, columns=cols)


setattr(VTS, "_dumpMACs", VTS.dumpMACs)
setattr(VTS, "dumpMACs", dumpMACs)

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
