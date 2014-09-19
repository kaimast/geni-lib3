# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import multiprocessing as MP
import time
import os
import traceback as tb
import tempfile

from geni.aggregate.apis import AMError, ListResourcesError

def checkavailrawpc(context, am):
  avail = []
  ad = am.listresources(context)
  for node in ad.nodes:
    if node.exclusive and node.available:
      if "raw-pc" in node.sliver_types:
        avail.append(node)
  return avail
  

def printlogininfo(context = None, am = None, slice = None, manifest = None):
  if not manifest:
    manifest = am.listresources(context, slice)
  for node in manifest.nodes:
    for login in node.logins:
      print "[%s] %s:%d" % (login.username, login.hostname, login.port)

  

# You can't put very much information in a queue before you hang your OS
# trying to write to the pipe, so we only write the paths and then load
# them again on the backside
def _mp_get_manifest (context, site, slc, q):
  try:
    mf = site.listresources(context, slc)
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(mf.text)
    path = tf.name
    tf.close()
    q.put((site.name, slc, path))
  except ListResourcesError:
    q.put((site.name, slc, None))
  except Exception, e:
    tb.print_exc()
    q.put((site.name, slc, None))

def getManifests (context, ams, slices):
  sitemap = {}
  for am in ams:
    sitemap[am.name] = am

  q = MP.Queue()
  for site in ams:
    for slc in slices:
      p = MP.Process(target=_mp_get_manifest, args=(context, site, slc, q))
      p.start()

  while MP.active_children():
    time.sleep(0.5)

  d = {}
  while not q.empty():
    (site,slc,mpath) = q.get()

    if mpath:
      am = sitemap[site]
      data = open(mpath).read()
      mf = am.amtype.parseManifest(data)
      d.setdefault(slc, {})[site] = mf

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

