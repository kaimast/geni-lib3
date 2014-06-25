# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import itertools

import geni.rspec.vts as VTS
import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import geni.aggregate.vts as VTSAM

import nbastin
context = nbastin.buildContext()

SLICE = "gec-20-demo"

vtsr = VTS.Request()

image = VTS.OVSOpenFlowImage("tcp:54.88.120.184:6633", ofver="1.3")
image.sflow = VTS.SFlow("54.88.120.184")

# Create all the empty datapaths and add them to the Request
dps = [VTS.Datapath(image, "dp%d" % (x)) for x in xrange(0,3)]
for dp in dps:
  vtsr.addResource(dp)

# Build the switch mesh
pairs = itertools.combinations(dps, 2)
for src,dst in pairs:
  VTS.connectInternalCircuit(src, dst)

#VTS.connectInternalCircuit(dps[0], dps[1])
#VTS.connectInternalCircuit(dps[0], dps[2])
#
# Add two host circuits
#dps[0].attachPort(VTS.PGCircuit())
#dps[1].attachPort(VTS.PGCircuit())
#dps[2].attachPort(VTS.PGCircuit())

# Write out the XML
vtsr.write("vts-demo.xml")

vtsm = VTSAM.DDC.createsliver(context, SLICE, vtsr)
IP = "10.50.1.%d"

pgr = PG.Request()
for idx, circuit in enumerate(vtsm.pg_circuits):
  vm = PG.XenVM("vm%d" % (idx))
  intf = vm.addInterface("if0")
  intf.addAddress(PG.IPv4Address(IP % (idx + 1), "255.255.255.0"))
  pgr.addResource(vm)

  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(circuit)
  pgr.addResource(lnk)
  
pgm = IG.UtahDDC.createsliver(context, SLICE, pgr)
for node in pgm.nodes:
  for login in node.logins:
    print "[%s] %s:%d" % (node.name, login.hostname, login.port)
