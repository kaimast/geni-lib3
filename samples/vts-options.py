# Copyright (c) 2013  Barnstormer Softworks, Ltd.

import json

import geni.rspec.pgmanifest as PGM

m = PGM.Manifest("vts-stage-manifest.xml")
for link in m.links:
  d = {"geni_sharelan_token" : "vts-segment-%s" % (link.client_id[4:]),
       "geni_sharelan_lanname" : link.client_id}
  f = open("%s.json" % (link.client_id), "w+")
  json.dump(d, f)
  f.close()
  
