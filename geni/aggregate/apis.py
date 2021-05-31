# Copyright (c) 2014-2018    Barnstormer Softworks, Ltd.

#    This Source Code Form is subject to the terms of the Mozilla Public
#    License, v. 2.0. If a copy of the MPL was not distributed with this
#    file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint: disable=too-many-arguments,fixme

import logging

from .frameworks import ClearinghouseError
from .core import APIRegistry
from .exceptions import AMError
from . import pgutil as ProtoGENI
from ..minigcf import amapi2 as AM2
from ..minigcf import amapi3 as AM3

# pylint: disable=multiple-statements
class AllocateError(AMError): pass
class CreateSliverError(AMError): pass
class DeleteSliverError(AMError): pass
class GetVersionError(AMError): pass
class ListResourcesError(AMError): pass
class ProvisionError(AMError): pass
class RenewSliverError(AMError): pass
class SliverStatusError(AMError): pass
class POAError(AMError): pass
# pylint: enable=multiple-statements

LOG = logging.getLogger("geni.aggregate.apis")

class AMAPIv3:
    @staticmethod
    def poa(context, url, sname, action, urns=None, options=None):
        sinfo = context.get_slice_info(sname)
        if not urns:
            urns = [sinfo.urn]

        res = AM3.poa(url, False, context.cf.cert, context.cf.key, [sinfo], urns, action, options)
        if res["code"]["geni_code"] == 0:
            return res["value"]

        if "am_type" in res["code"]:
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)

        raise POAError(res["output"], res)

    @staticmethod
    def paa (context, url, action, options = None):
        res = AM3.paa(url, False, context.cf.cert, context.cf.key, action, options)
        if res["code"]["geni_code"] == 0:
            return res["value"]

        raise POAError(res["output"], res)

    @staticmethod
    def allocate(context, url, sname, rspec, options=None):
        if options is None:
            options = {}
        sinfo = context.get_slice_info(sname)

        res = AM3.allocate(url, False, context.cf.cert, context.cf.key, [sinfo], sinfo.urn, rspec, options)
        if res["code"]["geni_code"] == 0:
            return res
        if "am_type" in res["code"]:
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)
        raise AllocateError(res["output"], res)

    @staticmethod
    def provision(context, url, sname, urns = None, options=None):
        if options is None:
            options = {}
        if urns is not None and not isinstance(urns, list):
            urns = [urns]

        sinfo = context.get_slice_info(sname)
        if not urns:
            urns = [sinfo.urn]

        res = AM3.provision(url, False, context.cf.cert, context.cf.key, [sinfo], urns, options)
        if res["code"]["geni_code"] == 0:
            return res
        if "am_type" in res["code"]:
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)
        raise ProvisionError(res["output"], res)

    @staticmethod
    def delete(context, url, sname, urns, options=None):
        if options is None:
            options = {}
        if not isinstance(urns, list):
            urns = [urns]

        sinfo = context.get_slice_info(sname)

        res = AM3.delete(url, False, context.cf.cert, context.cf.key, [sinfo], urns, options)
        if res["code"]["geni_code"] == 0:
            return res
        if res["code"].has_key("am_type"):
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)
        raise ProvisionError(res["output"], res)


class AMAPIv2:
    @staticmethod
    def list_resources(context, url, sname, options=None):
        if options is None:
            options = {}
        creds = []

        surn = None
        if sname:
            sinfo = context.get_slice_info(sname)
            surn = sinfo.urn
            creds.append(open(sinfo.path, "r", encoding="utf-8").read())

        creds.append(open(context.usercred_path, "r", encoding="utf-8").read())

        res = AM2.list_resources(url, False, context.cf.cert, context.cf.key,
                creds, options, surn)
        if res["code"]["geni_code"] == 0:
            return res
        if "am_type" in res["code"]:
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)

        raise ListResourcesError(res["output"], res)

    @staticmethod
    def create_sliver(context, url, sname, rspec):
        sinfo = context.get_slice_info(sname, create=True)
        cred_data = open(sinfo.path, "r", encoding="utf-8").read()

        LOG.debug("Creating slice with info %s", str(sinfo))

        udata = []
        for user in context.users:
            data = {"urn" : user.urn, "keys" : [open(x, "r", encoding="utf-8").read() for x in user.keys]}
            udata.append(data)

        res = AM2.create_sliver(url, False, context.cf.cert, context.cf.key, [cred_data], sinfo.urn, rspec, udata)
        if res["code"]["geni_code"] == 0:
            return res
        if "am_type" in res["code"]:
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)
        raise CreateSliverError(res["output"], res)

    @staticmethod
    def sliver_status(context, url, sname):
        sinfo = context.get_slice_info(sname)
        cred_data = open(sinfo.path, "r", encoding="utf-8").read()

        res = AM2.sliver_status(url, False, context.cf.cert, context.cf.key,
                [cred_data], sinfo.urn)
        if res["code"]["geni_code"] == 0:
            return res["value"]
        if "am_type" in res["code"]:
            if res["code"]["am_type"] == "protogeni":
                ProtoGENI.raiseError(res)
        raise SliverStatusError(res["output"], res)

    @staticmethod
    def renew_sliver(context, url, sname, date):
        sinfo = context.get_slice_info(sname)
        cred_data = open(sinfo.path, "r", encoding="utf-8").read()

        res = AM2.renew_sliver(url, False, context.cf.cert, context.cf.key,
                [cred_data], sinfo.urn, date)
        if res["code"]["geni_code"] == 0:
            return res["value"]
        raise RenewSliverError(res["output"], res)

    @staticmethod
    def delete_sliver(context, url, sname):
        try:
            sinfo = context.get_slice_info(sname)
            path = sinfo.path
        except ClearinghouseError as _:
            LOG.warning("Failed to get slice. Might have already expired.")

            # Slice is already gone. Delete local files, if any.
            context.delete_slice(sname, force=True)
            return 0 #TODO no sure what the return code here is for

        cred_data = open(path, "r", encoding="utf-8").read()

        res = AM2.delete_sliver(url, False, context.cf.cert, context.cf.key,
                [cred_data], sinfo.urn)
        if res["code"]["geni_code"] != 0:
            raise DeleteSliverError(res["output"], res)

        context.delete_slice(sname)
        return res["value"]

    @staticmethod
    def get_version(context, url):
        res = AM2.get_version(url, False, context.cf.cert, context.cf.key)
        if res["code"]["geni_code"] == 0:
            return res["value"]
        raise GetVersionError(res["output"], res)

APIRegistry.register("amapiv2", AMAPIv2())
APIRegistry.register("amapiv3", AMAPIv3())
