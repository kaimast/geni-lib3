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

class ColumnInfo(object):
  def __init__ (self, iname, oname, default = None, xform = None):
    self.iname = iname
    self.oname = oname
    self.default = default
    if xform:
      self.xform = xform
    else:
      self.xform = lambda x: x


def buildTable (rows, columns, spchar = "=", index_first = True, ignore_last = False):
  odata = []
  idx_list = []
  for row in rows:
    nrow = []
    if ignore_last:
      rdata = {"_last" : row[-1]}
      row = row[:-1]
    else:
      rdata = {}

    if index_first:
      idx_list.append(row[0])
      row = row[1:]
      
    for item in row:
      k,v = item.split(spchar)
      rdata[k] = v

    for col in columns:
      try:
        nrow.append(col.xform(rdata[col.iname]))
      except KeyError:
        nrow.append(col.default)

    odata.append(nrow)

  if idx_list:
    df = pandas.DataFrame.from_records(odata, columns = [x.oname for x in columns], index = idx_list)
  else:
    df = pandas.DataFrame.from_records(odata, columns = [x.oname for x in columns])

  return df


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

def replaceSymbol (module, name, func):
  """Moves module.name to module._name and sets module.name to the new function object."""
  setattr(module, "_%s" % (name), getattr(module, name))
  setattr(module, name, func)

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

def dumpFlows (self, context, sname, datapaths, **kwargs):
  if not isinstance(datapaths, list):
    datapaths = [datapaths]

  res = self._dumpFlows(context, sname, datapaths, **kwargs)
  data = []
  for k,v in res.iteritems():
    rows = [[y.strip(",") for y in x.split(" ")] for x in v]
    if len(rows) > 0:
      rows[0].insert(0, k)
    for row in rows[1:]:
      row.insert(0, '')
    data.extend(rows)

  cols = []
  cols.append(ColumnInfo("table_id", "table", default = 0, xform = int))
  cols.append(ColumnInfo("duration", "duration", xform = lambda x: int(x[:-1])))
  cols.append(ColumnInfo("priority", "priority", xform = int))
  cols.append(ColumnInfo("n_packets", "packets", default = 0, xform = int))
  cols.append(ColumnInfo("n_bytes", "bytes", default = 0, xform = int))
  cols.append(ColumnInfo("_last", "rule"))

  return buildTable(data, cols, ignore_last = True)


replaceSymbol(VTS, "dumpMACs", dumpMACs)
replaceSymbol(VTS, "dumpFlows", dumpFlows)

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
