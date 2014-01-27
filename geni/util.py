# Copyright (c) 2014  Barnstormer Softworks, Ltd.

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
    
