#!/usr/bin/env python

# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from multiprocessing import Process
from argparse import ArgumentParser

import example_config
import geni.aggregate.instageni as IG

context = example_config.buildContext()

def query_aggregate (context, site):
  try:
    ad = site.listresources(context)
    total = [node for node in ad.nodes if node.exclusive and "raw-pc" in node.sliver_types]
    avail = [node.component_id for node in ad.nodes if node.available and node.exclusive and "raw-pc" in node.sliver_types]
    print "[%s] (%d/%d)" % (site.name, len(avail), len(total))
#    print "[%s] %s" % (site.name, ", ".join(avail))
  except Exception:
    print "[%s] OFFLINE" % (site.name)
  

def do_parallel ():
  for idx,site in enumerate(IG.aggregates()):
    p = Process(target=query_aggregate, args=(context, site))
    p.start()


def do_serial ():
  for idx, site in enumerate(IG.aggregates()):
    query_aggregate(context, site)


def parse_args ():
  parser = ArgumentParser()
  parser.add_argument("--parallel", dest="parallel", default = False, action='store_true')
  opts = parser.parse_args()
  return opts

if __name__ == '__main__':
  opts = parse_args()

  if opts.parallel:
    do_parallel()
  else:
    do_serial()
