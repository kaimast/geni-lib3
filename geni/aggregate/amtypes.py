# Copyright (c) 2014-2017    Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import abc
import six

from .core import AMTypeRegistry
from ..rspec import pgad, pgmanifest, vtsmanifest, vtsad

class AMType:
    __metaclass__ = abc.ABCMeta

    def __init__ (self, name):
        self.name = name

    @abc.abstractmethod
    def parse_advertisement (self, data):
        return

    @abc.abstractmethod
    def parse_manifest (self, data):
        return


class ExoGENI(AMType):
    def __init__ (self, name="exogeni"):
        super().__init__(name)

    def parse_advertisement (self, data):
        return pgad.Advertisement(xml=data["value"])

    def parse_manifest (self, data):
        return pgmanifest.Manifest(xml = data["value"])


class ProtoGENI(AMType):
    def __init__ (self, name="pg"):
        super().__init__(name)

    def parse_advertisement(self, data):
        adv = pgad.Advertisement(xml=data["value"])
        adv.error_url = data["code"]["protogeni_error_url"]
        return adv

    def parse_manifest(self, data):
        if isinstance(data, (six.string_types)):
            manifest = pgmanifest.Manifest(xml = data)
        else:
            manifest = pgmanifest.Manifest(xml = data["value"])
            manifest.error_url = data["code"]["protogeni_error_url"]
        return manifest


class OpenGENI(AMType):
    def __init__ (self, name="opengeni"):
        super().__init__(name)

    def parse_advertisement(self, data):
        return pgad.Advertisement(xml=data["value"])

    def parse_manifest(self, data):
        return pgmanifest.Manifest(xml = data["value"])


class VTS(AMType):
    def __init__ (self, name="vts"):
        super().__init__(name)

    def parse_advertisement(self, data):
        return vtsad.Advertisement(xml=data["value"])

    def parse_manifest (self, data):
        if isinstance(data, (six.string_types)):
            manifest = vtsmanifest.Manifest(xml = data)
        else:
            manifest = vtsmanifest.Manifest(xml = data["value"])
        return manifest

AMTypeRegistry.register("opengeni", OpenGENI())
AMTypeRegistry.register("pg", ProtoGENI())
AMTypeRegistry.register("exogeni", ExoGENI())
AMTypeRegistry.register("vts", VTS())
