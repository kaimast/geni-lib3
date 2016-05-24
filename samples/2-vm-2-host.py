# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import geni.rspec.igutil as IGU
import geni.rspec.igext as IGX
from geni import util

import nbastin

class UnknownSharedVlan(Exception):
  def __init__ (self, name):
    self.name = name
  def __str__ (self):
    return "Shared VLAN %s is not known to this aggregate" % (self.name)


def main (sname, site, of_vlan = False, of_controller = None, shared_vlan = None):
  r = PG.Request()
  vms = []

  for idx in range(0,2):
    vm = PG.XenVM("vm%d" % (idx))
    vm.addInterface("if0")
    r.addResource(vm)
    vms.append(vm)

  lnk = PG.Link()
  lnk.addInterface(vms[0].interfaces[0])
  lnk.addInterface(vms[1].interfaces[0])
  r.addResource(lnk)
  if of_vlan:
    lnk.addChild(IGX.OFController(of_controller[0], of_controller[1]))
    
  context = nbastin.buildContext()
  ad = site.listresources(context)

  if shared_vlan:
    found_sv = False
    for sv in ad.shared_vlans:
      if sv.name == shared_vlan:
        lnk.connectSharedVlan(shared_vlan)
        found_sv = True
        break
    if not found_sv:
      raise UnknownSharedVlan(shared_vlan)
    
  vmnodes = []
  for node in ad.nodes:
    if IGU.shared_xen(node):
      vmnodes.append(node)

  for (vm, node) in zip(vms, vmnodes):
    vm.component_id = node.component_id

  m = site.createsliver(context, sname, r)
  f = open("%s-%s-manifest.xml" % (sname, site.name), "w+")
  f.write(m.text)
  f.close()

  util.printlogininfo(manifest = m)


if __name__ == '__main__':
  # Non-OF, will be restricted to 100Mbits/sec due to PG shaping
  main("test-2", IG.Stanford)

  # Private-OF
  #main("test-1", IG.Stanford, True, ("54.209.87.26", 7733))

  # FV-OF
  # main("test-1", IG.Stanford, False, None, "mesoscale-openflow")
