# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import abc
import os

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


class ExoGENI(AMType):
  def __init__ (self, name="exogeni"):
    super(ExoGENI, self).__init__ (name)

  def parseAdvertisement (self, data):
    return data

  def parseManifest (self, data):
    return data


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


class VTS(AMType):
  def __init__ (self, name="vts"):
    super(VTS, self).__init__(name)

  def parseAdvertisement (self, data):
    from geni.rspec import vtsad
    ad = vtsad.Advertisement(xml=data)
    return ad

  def parseManifest (self, data):
    from geni.rspec import vtsmanifest
    manifest = vtsmanifest.Manifest(xml = data)
    return manifest



AMTypeRegistry.register("foam", FOAM())
AMTypeRegistry.register("pg", ProtoGENI())
AMTypeRegistry.register("exogeni", ExoGENI())
AMTypeRegistry.register("vts", VTS())
