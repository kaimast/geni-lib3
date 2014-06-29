# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import geni.aggregate.apis

import nbastin

#context = nbastin.buildContext()
#context.debug = True

#try:
#  IG.GPO.deletesliver(context, "xen-test2")
#except geni.aggregate.apis.AMError, e:
#  pass

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
lnk.bandwidth = 1000000
lnk.disableMACLearning()

r.addResource(lnk)

r.write("dac.xml")

#manifest = IG.GPO.createsliver(context, "xen-test2", r)
#print manifest.text
