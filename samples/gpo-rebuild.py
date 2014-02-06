# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import itertools

import nbastin
import geni.aggregate.instageni
import geni.rspec.pg as PG

context = nbastin.buildContext()
am = geni.aggregate.instageni.GPO

#am.deletesliver(context, "vts-stage")
ad = am.listresources(context)

vtsvlans = []
for vlan in ad.shared_vlans:
  if vlan.name.startswith("vts"):
    vtsvlans.append(vlan.name)

r = PG.Request()

node = PG.RawPC("vts")
node.disk_image = "urn:publicid:IDN+instageni.gpolab.bbn.com+image+emulab-ops:UBUNTU12-64-STD"

intfs = []
for idx in xrange(1,4):
  intf = node.addInterface("if%d" % (idx))
  intf.component_id = "eth%d" % (idx)
  intfs.append(intf)
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan("mesoscale-openflow")
  r.addResource(lnk)

pairs = zip(itertools.cycle(intfs), vtsvlans)
for (intf, vlan) in pairs:
  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(vlan)
  r.addResource(lnk)

r.addResource(node)

mfest = am.createsliver(context, "vts-stage", r)
print mfest.text
print mfest
