# Copyright (c) 2014  Barnstormer Softworks, Ltd.

class AbstractImplementationError(Exception):
  def __str__ (self):
    return "Called unimplemented abstract method"

class NoUserError(Exception):
  def __str__ (self):
    return "No framework user specified"

class SliceCredError(Exception):
  def __init__ (self, text):
    self.text = text

  def __str__ (self):
    return text

class WrongNumberOfArgumentsError(Exception):
  def __str__ (self):
    return "Called a function with the wrong number of arguments"
