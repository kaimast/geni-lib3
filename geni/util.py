# Copyright (c) 2014  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import multiprocessing as MP
import time
import os
import traceback as tb
import tempfile

from geni.aggregate.apis import AMError, ListResourcesError, DeleteSliverError

def checkavailrawpc(context, am):
  """Returns a list of node objects representing available raw PCs at the
given aggregate."""

  avail = []
  ad = am.listresources(context)
  for node in ad.nodes:
    if node.exclusive and node.available:
      if "raw-pc" in node.sliver_types:
        avail.append(node)
  return avail
  

def printlogininfo(context = None, am = None, slice = None, manifest = None):
  """Prints out host login info in the format:
::
  [username] hostname:port

If a manifest object is provided the information will be mined from this data,
otherwise you must supply a context, slice, and am and a manifest will be
requested from the given aggregate."""

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
  """Returns a two-level dictionary of the form:
::
  {slice_name : { site_object : manifest_object, ... }, ...}

Containing the manifests for all provided slices at all the provided
sites.  Requests are made in parallel and the function blocks until the
slowest site returns (or times out)."""

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
  """Returns a dictionary of the form:
::
  { site_object : advertisement_object, ...}

Containing the advertisements for all the requested aggregates.  Requests
are made in parallel and the function blocks until the slowest site
returns (or times out).

.. warning::
  Particularly large advertisements may break the shared memory queue
  used by this function."""


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


def deleteSliverExists(am, context, slice):
  """Attempts to delete all slivers for the given slice at the given AM, suppressing all returned errors."""
  try:
    am.deletesliver(context, slice)
  except DeleteSliverError:
    pass

def builddot (manifests, path):
  """Constructs a dotfile of the topology described in the passed in manifest list and saves it at `path`."""

  from .rspec import vtsmanifest as VTSM
  from .rspec.pgmanifest import Manifest as PGM

  dot_data = []
  dda = dot_data.append # Save a lot of typing

  dda("digraph {")

  for manifest in manifests:
    if isinstance(manifest, PGM):
      intf_map = {}
      for node in manifest.nodes:
        dda("\"%s\" [label = \"%s\"]" % (node.component_id, node.name))
        for interface in node.interfaces:
          intf_map[interface.sliver_id] = node.component_id

      for link in manifest.links:
        lannode = link.client_id
        if link.vlan:
          lannode = "%s" % (link.vlan)

        for ref in link.interface_refs:
          dda("\"%s\" -- \"%s\"" % (intf_map[ref], lannode))
        
    elif isinstance(manifest, VTSM.Manifest):
      # TODO: We need to actually go through datapaths and such, but we can approximate for now
      for port in manifest.ports:
        if isinstance(port, VTSM.GREPort):
          pass
        elif isinstance(port, VTSM.PGLocalPort):
          dda("\"%s\" -- \"%s\"" % (port.dpname, port.shared_vlan))
        elif isinstance(port, VTSM.InternalPort):
          dda("\"%s\" -> \"%s\"" % (port.dpname, port.remote_dpname))
        else:
          continue ### TODO: Unsupported Port Type

  dda("}")

  return "\n".join(dot_data)

