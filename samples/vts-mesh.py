import itertools
import geni.rspec.vts as VTS

r = VTS.Request()

image = VTS.OVSOpenFlowImage("tcp:192.0.2.1:6633")
image.sflow = VTS.SFlow("192.0.2.1")

# Create all the empty datapaths and add them to the Request
dps = [VTS.Datapath(image, "dp%d" % (x)) for x in xrange(0,4)]
for dp in dps:
  r.addResource(dp)

# Build the switch mesh
pairs = itertools.combinations(dps, 2)
for src,dst in pairs:
  sp = VTS.InternalCircuit(None)
  dp = VTS.InternalCircuit(None)
  src.attachPort(sp)
  dst.attachPort(dp)
  sp.target = dp.clientid
  dp.target = sp.clientid

# Add two host circuits
dps[0].attachPort(VTS.PGCircuit())
dps[1].attachPort(VTS.PGCircuit())

# Write out the XML
r.write("vts-mesh.xml")
