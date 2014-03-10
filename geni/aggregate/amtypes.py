# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import abc

from .core import AMTypeRegistry

class AMType(object):
  __metaclass__ = abc.ABCMeta

  def __init__ (self, name):
    self.name = name

  @abc.abstractmethod
  def parseAdvertisement (self, data):
    return

  @abc.abstractmethod
  def parseManifest (self, data):
    return


class ProtoGENI(AMType):
  def __init__ (self, name="pg"):
    super(ProtoGENI, self).__init__(name)

  def parseAdvertisement (self, data):
    from geni.rspec import pgad
    ad = pgad.Advertisement(xml=data)
    return ad

  def parseManifest (self, data):
    from geni.rspec import pgmanifest
    manifest = pgmanifest.Manifest(xml = data)
    return manifest


class FOAM(AMType):
  def __init__ (self, name="foam"):
    super(FOAM, self).__init__(name)

  def parseAdvertisement (self, data):
    from geni.rspec import ofad
    ad = ofad.Advertisement(xml=data)
    return ad

  def parseManifest (self, data):
    from geni.rspec import ofmanifest
    manifest = ofmanifest.Manifest(xml = data)
    return manifest


AMTypeRegistry.register("foam", FOAM())
AMTypeRegistry.register("pg", ProtoGENI())
