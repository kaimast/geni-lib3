# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import sys
import inspect

from .core import AM, APIRegistry

class VTS(AM):
  def __init__ (self, name, host, url = None):
    self.host = host
    if url is None:
      url = "https://%s:3626/foam/gapi/2" % (host)
    self.urlv3 = "%s3" % (url[:-1])
    self._apiv3 = APIRegistry.get("amapiv3")
    super(VTS, self).__init__(name, url, "amapiv2", "vts")

  def changeController (self, context, sname, url, datapaths, ofver=None):
    options={"controller-url" : url, "datapaths" : datapaths}
    if ofver:
      options["openflow-version"] = ofver
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:change-controller", options)

  def dumpFlows (self, context, sname, datapaths, show_hidden=False):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:dump-flows",
                           options={"datapaths" : datapaths, "show-hidden" : show_hidden})

  def dumpMACs (self, context, sname, datapaths):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:l2:dump-macs",
                           options={"datapaths" : datapaths})

  def clearFlows (self, context, sname, datapaths):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:clear-flows", options={"datapaths" : datapaths})

  def portDown (self, context, sname, client_id):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:port-down",
                           options={"port-client-id" : client_id})

  def portUp (self, context, sname, client_id):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:port-up",
                           options={"port-client-id" : client_id})

  def addFlows (self, context, sname, flows):
    return self._apiv3.poa(context, self.urlv3, sname, "vts:of:add-flows", options={"rules" : flows})

  def getSTPInfo (self, context, sname, datapaths):
    if not isinstance(datapaths, list): datapaths = [datapaths]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:l2:stp-info",
                           options={"datapaths" : datapaths})

  def getPortInfo (self, context, sname, datapaths):
    if not isinstance(datapaths, list): datapaths = [datapaths]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:get-port-info",
                           options={"datapaths" : datapaths})

  def getLeaseInfo (self, context, sname, client_ids):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:uh.simple-dhcpd:get-leases",
                           options = {"client-ids" : client_ids})

  def setPortVLAN (self, context, sname, port_tuples):
    if not isinstance(port_tuples, list): port_tuples = [port_tuples]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:set-vlan",
                           options = {"ports" : port_tuples})

  def setPortTrunk (self, context, sname, port_list):
    if not isinstance(port_list, list): port_list = [port_list]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:raw:set-trunk",
                           options = {"ports" : port_list})

  def addSSHKeys (self, context, sname, client_ids, keys):
    if not isinstance(client_ids, list): client_ids = [client_ids]
    if not isinstance(keys, list): keys = [keys]
    return self._apiv3.poa(context, self.urlv3, sname, "vts:container:add-keys",
                           options = {"client-ids" : client_ids, "ssh-keys" : keys})

  def setDHCPSubnet (self, context, sname, subnet_tuples):
    if not isinstance(subnet_tuples, list): subnet_tuples = [subnet_tuples]
    clid_map = {}
    for clid,subnet in subnet_tuples:
      clid_map[clid] = subnet

    return self._apiv3.poa(context, self.urlv3, sname, "vts:uh.simple-dhcpd:set-subnet",
                           options = {"client-id-map" : clid_map})



DDC = VTS("vts-ddc", "ddc.vts.bsswks.net")
Clemson = VTS("vts-clemson", "clemson.vts.bsswks.net")
GPO = VTS("vts-gpo", "gpo.vts.bsswks.net")
Illinois = VTS("vts-illinois", "uiuc.vts.bsswks.net")
MAX = VTS("vts-max", "max.vts.bsswks.net")
NPS = VTS("vts-nps", "nps.vts.bsswks.net")
UKYPKS2 = VTS("vts-ukypks2", "ukypks2.vts.bsswks.net")
UtahDDC = DDC
StarLight = VTS("vts-starlight", "starlight.vts.bsswks.net")
UH = VTS("vts-uh", "uh.vts.bsswks.net")
UWashington = VTS("vts-uwashington", "uwash.vts.bsswks.net")


def aggregates ():
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      yield obj

def name_to_aggregate ():
  result = dict()
  module = sys.modules[__name__]
  for _,obj in inspect.getmembers(module):
    if isinstance(obj, AM):
      result[obj.name] = obj
  return result
