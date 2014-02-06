# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import nbastin

context = nbastin.buildContext()

r = PG.Request()

vm1 = PG.XenVM("xen1")
intf1 = vm1.addInterface("if0")
r.addResource(vm1)

vm2 = PG.XenVM("xen2")
intf2 = vm2.addInterface("if0")
r.addResource(vm2)

lnk = PG.Link()
lnk.addInterface(intf1)
lnk.addInterface(intf2)

r.addResource(lnk)

manifest = IG.GPO.createsliver(context, "xen-test2", r)
print manifest.text
