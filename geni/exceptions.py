# Copyright (c) 2014  Barnstormer Softworks, Ltd.

class AbstractImplementationError(Exception):
  def __str__ (self):
    return "Called unimplemented abstract method"
