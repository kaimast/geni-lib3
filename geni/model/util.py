# Copyright (c) 2014  Barnstormer Softworks, Ltd.

class XPathXRange(object):
  def __init__ (self, xp, klass):
    self._data = xp
    self._klass = klass
  def __iter__ (self):
    for obj in self._data:
      yield self._klass._fromdom(obj)
  def __len__ (self):
    return len(self._data)
  def __getitem__ (self, idx):
    return self._klass._fromdom(self._data[idx])
