# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

import nbastin
context = nbastin.buildContext()

SLICENAME = "test-1"

r = PG.Request()
vm = PG.XenVM("xen1")
r.addResource(vm)

m = IG.UtahDDC.createsliver(context, SLICENAME, r)

for node in m.nodes:
  for login in node.logins:
    print "[%s] %s:%d" % (login.username, login.hostname, login.port)

