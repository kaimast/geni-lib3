import geni.rspec.pg as PG
import geni.rspec.pgad

DISK_IMAGE = "urn:publicid:IDN+instageni.gpolab.bbn.com+image+emulab-ops:UBUNTU12-64-STD"

xenshared = []
ad = geni.rspec.pgad.Advertisement("rspec-utahddc-geniracks-net.xml")
for node in ad.nodes:
  if node.available and node.shared:
    if "emulab-xen" in node.sliver_types:
      xenshared.append(node)

r = PG.Request()

n1 = PG.XenVM("xen1", component_id = xenshared[0].component_id)
n1.disk_image = DISK_IMAGE

n2 = PG.XenVM("xen2", component_id = xenshared[1].component_id)
n2.disk_image = DISK_IMAGE

r.addResource(n1)
r.addResource(n2)

for lan in xrange(0, 45):
  i1 = n1.addInterface("if%d" % (lan))
  i2 = n2.addInterface("if%d" % (lan))
  i1.bandwidth = 10000
  i2.bandwidth = 10000
  lnk = PG.LAN("lan-%d" % (lan))
  lnk.addInterface(i1)
  lnk.addInterface(i2)
  r.addResource(lnk)

r.write("pwe-build.xml")
