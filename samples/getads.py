#!/usr/bin/env python

# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import multiprocessing as MP
from argparse import ArgumentParser
import time

import example_config
import geni.aggregate.instageni as IG

context = example_config.buildContext()

def get_advertisement (context, site):
  try:
    ad = site.listresources(context)
    f = open("%s-ad.xml" % (site.name), "w+")
    f.write(ad.text)
    f.close()
    print "[%s] Done" % (site.name)
  except:
    print "[%s] OFFLINE" % (site.name)
  

def do_parallel ():
  for idx,site in enumerate(IG.aggregates()):
    p = MP.Process(target=get_advertisement, args=(context, site))
    p.start()

if __name__ == '__main__':
  do_parallel()
