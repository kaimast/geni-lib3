# Copyright (c) 2014  Barnstormer Softworks, Ltd.

import geni.util
import nbastin
import time

import geni.aggregate.instageni as IG

if __name__ == '__main__':
  context = nbastin.buildContext()

  while True:
    avail = geni.util.checkavailrawpc(context, IG.MAX)
    print "%s: %d" % (time.ctime(), len(avail))
    time.sleep(20)
