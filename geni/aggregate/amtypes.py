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
    from ..rspec import pgad
    ad = pgad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import pgmanifest
    manifest = pgmanifest.Manifest(xml = data["value"])
    return manifest


class ProtoGENI(AMType):
  def __init__ (self, name="pg"):
    super(ProtoGENI, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import pgad
    ad = pgad.Advertisement(xml=data["value"])
    ad.error_url = data["code"]["protogeni_error_url"]
    return ad

  def parseManifest (self, data):
    from ..rspec import pgmanifest
    manifest = pgmanifest.Manifest(xml = data["value"])
    manifest.error_url = data["code"]["protogeni_error_url"]
    return manifest


class FOAM(AMType):
  def __init__ (self, name="foam"):
    super(FOAM, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import ofad
    ad = ofad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import ofmanifest
    manifest = ofmanifest.Manifest(xml = data["value"])
    return manifest


class OpenGENI(AMType):
  def __init__ (self, name="opengeni"):
    super(OpenGENI, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import pgad
    ad = pgad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import pgmanifest
    manifest = pgmanifest.Manifest(xml = data["value"])
    return manifest


class VTS(AMType):
  def __init__ (self, name="vts"):
    super(VTS, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import vtsad
    ad = vtsad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import vtsmanifest
    manifest = vtsmanifest.Manifest(xml = data["value"])
    return manifest


class OESS(AMType):
  def __init__ (self, name="oess"):
    super(OESS, self).__init__(name)

  def parseAdvertisement (self, data):
    from ..rspec import oessad
    ad = oessad.Advertisement(xml=data["value"])
    return ad

  def parseManifest (self, data):
    from ..rspec import oessmanifest
    manifest = oessmanifest.Manifest(xml = data["value"])
    return manifest


AMTypeRegistry.register("foam", FOAM())
AMTypeRegistry.register("opengeni", OpenGENI())
AMTypeRegistry.register("pg", ProtoGENI())
AMTypeRegistry.register("exogeni", ExoGENI())
AMTypeRegistry.register("vts", VTS())
AMTypeRegistry.register("oess", OESS())
