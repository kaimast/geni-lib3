# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import multiprocessing as MP
import time

import geni.aggregate.instageni as IG
import geni.util

context = geni.util.loadContext(key_passphrase = True)

OVERLOAD = 38

def query_aggregate (context, site, q):
  try:
    res = []
    ad = site.listresources(context)
    for node in ad.nodes:
      if not node.exclusive:
        try:
          if "emulab-xen" in node.sliver_types:
            res.append((node.component_id, node.hardware_types["pcvm"], "Xen"))
          else:
            res.append((node.component_id, node.hardware_types["pcvm"], "OpenVZ"))
        except:
          continue
    q.put((site.name, res))
  except Exception:
    q.put((site.name, ["OFFLINE"]))


def do_parallel ():
  q = MP.Queue()
  for site in IG.aggregates():
    p = MP.Process(target=query_aggregate, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(0.5)

  l = []
  while not q.empty():
    l.append(q.get())

  xen_avail = xen_total = 0
  vz_avail = vz_total = 0

  overload_cids = []
  underload_cids = []

  for idx,pair in enumerate(l):
    site_vz = site_xen = 0
    entries = []

    (site_name, res) = pair
    for (cid, count, typ) in res:
      if typ == "Xen":
        used = 100 - int(count)
        site_xen += used
        if used >= OVERLOAD:
          overload_cids.append(cid)
        else:
          underload_cids.append(cid)
        xen_avail += int(count)
        xen_total += 100 
      elif typ == "OpenVZ":
        site_vz += 100 - int(count)
        vz_avail += int(count)
        vz_total += 100
      entries.append("   [%s] %s/100 (%s)" % (cid, count, typ))
    print "%02d %s (Used: %d Xen, %d OpenVZ)" % (idx+1, site_name, site_xen, site_vz)
    for entry in entries:
      print entry

  print "OpenVZ: %d/%d" % (vz_avail, vz_total)
  print "Xen: %d/%d" % (xen_avail, xen_total)

  print "Overloaded hosts: %d" % (len(overload_cids))
  print "Underloaded hosts: %d" % (len(underload_cids))

if __name__ == '__main__':
  do_parallel()
