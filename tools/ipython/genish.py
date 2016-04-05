# Copyright (c) 2015  Barnstormer Softworks, Ltd.

# genish as an iPython extension for use with Jupyter

import types

import graphviz
import pandas
import wrapt

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
  g = graphviz.Source(dotstr)
  g.engine = "circo"
  return g


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
### Converters
#####

STP_PORT_ROW = """<tr>
<td>%(client-id)s (%(num)d)</td><td>%(stp_state)s</td><td>%(stp_role)s</td><td>%(stp_port_id)s</td><td>%(stp_sec_in_state)s</td>
<td>%(stp_rx_count)d</td><td>%(stp_tx_count)d</td><td>%(stp_error_count)d</td>
</tr>"""

class STPProxy(wrapt.ObjectProxy):
  def _repr_html_ (self):
    brt = """
  <table>
    <tr><th colspan="3" scope="row">Bridge: <b>%(client-id)s</b></th></tr>
    <tr><th>Bridge ID</th><th>Designated Root</th><th>Root Path Cost</th></tr>
    <tr><td>%(stp_bridge_id)s</td><td>%(stp_designated_root)s</td><td>%(stp_root_path_cost)s</td></tr>
  </table>""" % (self)
    pelist = []
    for port in self["ports"]:
      d = {}
      d.update(port)
      d.update(port["info"])
      pe = STP_PORT_ROW % (d)
      pelist.append(pe)
    pt = """
  <table>
    <tr><th>Port</th><th>State</th><th>Role</th><th>Port ID</th><th>In State (secs)</th><th>RX</th><th>TX</th><th>Errors</th></tr>
    %s
  </table>
  """ % ("\n".join(pelist))
    return "%s\n%s" % (brt,pt)


class RetListProxy(object):
  def __init__ (self, obj, columns, row_template):
    self._obj = obj
    self._columns = columns
    self._row_template = row_template
    self._col_template = "<th>%s</th>"

  def __len__ (self):
    return len(self._obj)

  def __getitem__ (self, i):
    return self._obj[i]

  def __getslice__ (self, i, j):
    i = max(i, 0); j = max(j, 0)
    return self._obj[i:j]

  def __contains__ (self, item):
    return item in self._obj

  def __iter__ (self):
    for x in self._obj:
      yield x

  def _repr_html_ (self):
    trlist = []
    for row in self._obj:
      trlist.append(self._row_template.format(**row))

    collist = []
    for column in self._columns:
      collist.append(self._col_template % (column))

    return """<table>\n<tr>%s</tr>\n%s\n<table""" % ("".join(collist), "\n".join(trlist))
      

LEASEROW = "<tr><td>{hostname}</td><td>{ip-address}</td><td>{mac-address}</td><td>{binding-state}</td><td>{end:%Y-%m-%d %H:%M:%S}</td></tr>"
LEASECOLS = ["Hostname", "IP Address", "MAC Address", "State", "End"]

PINFOCOLS = ["Client ID", "ifindex", "vlan", "MTU", "Admin State", "Link State", "RX Bytes (Pkts)", "TX Bytes (Pkts)"]
PINFOROW = "<tr><td>{client-id}</td><td>{ifindex}</td><td>{tag}</td><td>{mtu}</td><td>{admin_state}</td><td>{link_state}</td><td>{statistics[rx_bytes]} ({statistics[rx_packets]})</td><td>{statistics[tx_bytes]} ({statistics[tx_packets]})</td></tr>"

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

def getSTPInfo (self, context, sname, datapaths):
  if not isinstance(datapaths, list):
    datapaths = [datapaths]

  res = self._getSTPInfo(context, sname, datapaths)
  retobj = {}
  for br in res:
    retobj[br["client-id"]] = STPProxy(br)
  return retobj

def getLeaseInfo (self, context, sname, client_ids):
  if not isinstance(client_ids, list):
    client_ids = [client_ids]

  res = self._getLeaseInfo(context, sname, client_ids)
  retobj = {}
  for k,v in res.items():
    retobj[k] = RetListProxy(v, LEASECOLS, LEASEROW)
  return retobj

def getPortInfo (self, context, sname, client_ids):
  res = self._getPortInfo(context, sname, client_ids)
  retobj = {}
  for k,v in res.items():
    retobj[k] = RetListProxy(v, PINFOCOLS, PINFOROW)
  return retobj


replaceSymbol(VTS, "dumpMACs", dumpMACs)
replaceSymbol(VTS, "dumpFlows", dumpFlows)
replaceSymbol(VTS, "getSTPInfo", getSTPInfo)
replaceSymbol(VTS, "getLeaseInfo", getLeaseInfo)
replaceSymbol(VTS, "getPortInfo", getPortInfo)

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
