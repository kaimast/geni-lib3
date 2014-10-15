# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# Builds two vms at different sites, each connected to a local L2 datapath
# The datapaths at each site are then connected to each other over the WAN
# using a GRE tunnel over the "geni-core" circuit plane

import geni.rspec.vts as VTS
import geni.rspec.pg as PG
import geni.aggregate.instageni as IG
import geni.aggregate.vts as VTSAM
import geni.util

import nbastin
context = nbastin.buildContext()

SLICE = "gec-20-demo"

# Delete the slivers if they already exist
geni.util.deleteSliverExists(VTSAM.GPO, context, SLICE)
geni.util.deleteSliverExists(VTSAM.Illinois, context, SLICE)
geni.util.deleteSliverExists(IG.GPO, context, SLICE)
geni.util.deleteSliverExists(IG.Illinois, context, SLICE)

# Build the non-OF OVS image for each site
image = VTS.OVSL2Image()

# Get advertisements so we can get circuit-plane info
gpoad = VTSAM.GPO.listresources(context)
uiucad = VTSAM.Illinois.listresources(context)

# Build VTS request at Illinois
uiucvtsr = VTS.Request()
dp = VTS.Datapath(image, "dp-uiuc")
dp.attachPort(VTS.PGCircuit())
for cp in gpoad.circuit_planes:
  if cp.label == "geni-core":
    uiuc_wan_port = VTS.GRECircuit("geni-core", cp.endpoint)
    dp.attachPort(uiuc_wan_port)
uiucvtsr.addResource(dp)
uiucvtsr.write("uiuc-vts-request.xml")

# Make the VTS Reservation at Illinois
uiucvtsm = VTSAM.Illinois.createsliver(context, SLICE, uiucvtsr)
uiucvtsm.write("uiuc-vts-manifest.xml")

# Build the PG Request at Illinois using the circuit information from the VTS manifest
uiucpgr = PG.Request()
for idx, circuit in enumerate(uiucvtsm.pg_circuits):
  vm = PG.XenVM("vm%d" % (idx))
  intf = vm.addInterface("if0")
  intf.addAddress(PG.IPv4Address("172.16.5.1", "255.255.255.0"))
  uiucpgr.addResource(vm)

  lnk = PG.Link()
  lnk.addInterface(intf)
  lnk.connectSharedVlan(circuit)
  uiucpgr.addResource(lnk)
uiucpgr.write("uiuc-ig-request.xml")

# Build the VTS request for GPO
gpovtsr = VTS.Request()
dp = VTS.Datapath(image, "dp-gpo")
dp.attachPort(VTS.PGCircuit())
dp.attachPort(VTS.GRECircuit("geni-core", uiucvtsm.findPort(uiuc_wan_port.clientid).local_endpoint))
gpovtsr.addResource(dp)
gpovtsr.write("gpo-vts-request.xml")

# Make the VTS reservation at GPO
gpovtsm = VTSAM.GPO.createsliver(context, SLICE, gpovtsr)
gpovtsm.write("gpo-vts-manifest.xml")
