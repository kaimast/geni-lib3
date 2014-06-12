# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import geni.aggregate.apis

import nbastin
context = nbastin.buildContext()

IG.UtahDDC.deletesliver(context, "xen-test3")

r = PG.Request()

vm1 = PG.XenVM("xen1")
intf1 = vm1.addInterface("if0")
intf1.component_id = "eth1"
r.addResource(vm1)

vm2 = PG.XenVM("xen2")
intf2 = vm2.addInterface("if1")
intf2.component_id = "eth2"
r.addResource(vm2)

lnk = PG.Link()
lnk.addInterface(intf1)
lnk.addInterface(intf2)

r.addResource(lnk)

r.write("dac.xml")

manifest = IG.UtahDDC.createsliver(context, "xen-test3", r)
print manifest.text
