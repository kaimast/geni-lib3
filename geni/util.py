# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import multiprocessing as MP
import time

from geni.aggregate.apis import AMError

def checkavailrawpc(context, am):
  avail = []
  ad = am.listresources(context)
  for node in ad.nodes:
    if node.exclusive and node.available:
      if "raw-pc" in node.sliver_types:
        avail.append(node)
  return avail
  

def printlogininfo(context, am, slice):
  manifest = am.listresources(context, slice)
  for node in manifest.nodes:
    for login in node.logins:
      print "[%s] %s:%d" % (login.username, login.hostname, login.port)
  

def getManifests (context, am, slices):
  d = {}
  for slice in slices:
    try:
      d[slice] = am.listresources(context, slice)
    except AMError:
      continue

  return d

def _mp_get_advertisement (context, site, q):
  try:
    ad = site.listresources(context)
    q.put((site.name, ad))
  except:
    q.put((site.name, None))
    

def getAdvertisements (context, ams):
  q = MP.Queue()
  for site in ams:
    p = MP.Process(target=_mp_get_advertisement, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(0.5)

  d = {}
  while not q.empty():
    (site,ad) = q.get()
    d[site] = ad

  return d

