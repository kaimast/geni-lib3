import geni.rspec.pg as PG
import geni.aggregate.instageni as IG

import nbastin
context = nbastin.buildContext()

NETMASK = "255.255.255.0"
IPS = ["10.20.30.1", "10.20.30.2", "10.20.30.3"]

for site in IG.aggregates():
  if site is IG.UtahDDC:
    continue

  try:
    ad = site.listresources(context)
  except Exception:
    # Continue past aggregates that are down
    continue

  r = PG.Request()
  intfs = []

  # Xen VMs
  for (idx, node) in enumerate([node for node in ad.nodes if not node.exclusive and "emulab-xen" in node.sliver_types]):
    vm = PG.XenVM("xen%d" % (idx))
    intf = vm.addInterface("if0")
    intf.addAddress(PG.IPv4Address(IPS[idx], NETMASK))
    r.addResource(vm)
    intfs.append(intf)
    vm.component_id = node.component_id

  # VZNode
  # Sorry about the stupidity about how to find OpenVZ hosts.  I should fix this.
  vznode = [node for node in ad.nodes if not node.exclusive and "emulab-xen" not in node.sliver_types and node.hardware_types.has_key("pcvm")][0]
  vzc = PG.VZContainer("vz0")
  intf = vzc.addInterface("if0")
  intf.addAddress(PG.IPv4Address(IPS[2], NETMASK))
  r.addResource(vzc)
  intfs.append(intf)
  vzc.component_id = vznode.component_id

  # Controller
  cvm = PG.XenVM("controller")
  cvm.routable_control_ip = True
  cvm.addService(PG.Install(url="http://www.gpolab.bbn.com/experiment-support/OpenFlowHW/of-hw.tar.gz", path="/local"))
  cvm.addService(PG.Execute(shell="sh", command = "sudo /local/install-script.sh"))
  r.addResource(cvm)

  # Big LAN!
  lan = PG.LAN()
  for intf in intfs:
    lan.addInterface(intf)
  lan.connectSharedVlan("mesoscale-openflow")
  r.addResource(lan)

  r.write("%s.xml" % (site.name))
