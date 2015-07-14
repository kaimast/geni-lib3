# Copyright (c) 2014  Barnstormer Softworks, Ltd.

def shared_xen (node):
  if not node.exclusive:
    if "emulab-xen" in node.sliver_types:
      return True
  return False
