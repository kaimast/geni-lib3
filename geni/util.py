# Copyright (c) 2014-2018  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint: disable=too-many-arguments,fixme

import datetime
import json
import multiprocessing as MP
import os
import os.path
import shutil
import subprocess
import tempfile
import time
import traceback as tb
import zipfile
import logging
import six
import getpass

from .aggregate.apis import ListResourcesError, DeleteSliverError
import geni._coreutil as GCU
from .aggregate.spec import AMSpec

LOG = logging.getLogger('geni.util')

def _getdefault(obj, attr, default):
    if hasattr(obj, attr):
        return obj[attr]
    return default

def checkavailrawpc(context, am):
    """Returns a list of node objects representing available raw PCs at the
given aggregate."""

    avail = []
    ad = am.listresources(context)
    for node in ad.nodes:
        if node.exclusive and node.available:
            if "raw-pc" in node.sliver_types:
                avail.append(node)
    return avail


def get_login_info(manifest):
    ''' Returns the login information (username and address) for all machines in the specified manifest '''

    #pylint: disable=import-outside-toplevel
    from .rspec.vtsmanifest import Manifest as VTSM
    from .rspec.pgmanifest import Manifest as PGM

    linfo = {}
    if isinstance(manifest, PGM):
        for node in manifest.nodes:
            logins = []

            for login in node.logins:
                logins.append({
                    "username": login.username,
                    "hostname": login.hostname,
                    "port": login.port
                })

            linfo[node.client_id] = logins
    elif isinstance(manifest, VTSM):
        for container in manifest.containers:
            logins = []

            for login in container.logins:
                logins.append({
                    "username": login.username,
                    "hostname": login.hostname,
                    "port": login.port
                })

            linfo[container.client_id] = logins
    return linfo


def print_login_info(context = None, am = None, sname = None, manifest = None):
    """Prints out host login info in the format:
::
    [client_id][username] hostname:port

If a manifest object is provided the information will be mined from this data,
otherwise you must supply a context, slice, and am and a manifest will be
requested from the given aggregate."""

    if not manifest:
        manifest = am.listresources(context, sname)

    infos = get_login_info(manifest)
    for (client_id, logins) in infos.items():
        for info in logins:
            print(f'[{client_id}][{info["username"]}] {info["hostname"]}:{info["port"]}')


# You can't put very much information in a queue before you hang your OS
# trying to write to the pipe, so we only write the paths and then load
# them again on the backside
def _mp_get_manifest(context, site, slc, queue):
    try:
        # Don't use geni.tempfile here - we don't want them deleted when the child process ends
        # TODO: tempfiles should get deleted when the parent process picks them back up
        mf = site.listresources(context, slc)
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(mf.text)
            path = file.name

        queue.put((site.name, slc, path))
    except ListResourcesError:
        queue.put((site.name, slc, None))
    except Exception:
        tb.print_exc()
        queue.put((site.name, slc, None))

def getManifests(context, ams, slices):
    """Returns a two-level dictionary of the form:
::
    {slice_name : { site_object : manifest_object, ... }, ...}

Containing the manifests for all provided slices at all the provided
sites.    Requests are made in parallel and the function blocks until the
slowest site returns (or times out)."""

    sitemap = {}
    for am in ams:
        sitemap[am.name] = am

    queue = MP.Queue()
    for site in ams:
        for slc in slices:
            proc = MP.Process(target=_mp_get_manifest, args=(context, site, slc, queue))
            proc.start()

    while MP.active_children():
        time.sleep(0.5)

    d = {}
    while not queue.empty():
        (site, slc, mpath) = queue.get()

        if mpath:
            with open(mpath) as file:
                am = sitemap[site]
                data = file.read()
                mf = am.amtype.parseManifest(data)
                d.setdefault(slc, {})[sitemap[site]] = mf

    return d


def _mp_get_advertisement(context, site, queue):
    try:
        ad = site.listresources(context)
        queue.put((site.name, ad))
    except Exception:
        queue.put((site.name, None))

def get_advertisements(context, ams):
    """Returns a dictionary of the form:
::
    { site_object : advertisement_object, ...}

Containing the advertisements for all the requested aggregates.    Requests
are made in parallel and the function blocks until the slowest site
returns (or times out).

.. warning::
    Particularly large advertisements may break the shared memory queue
    used by this function."""


    queue = MP.Queue()
    for site in ams:
        proc = MP.Process(target=_mp_get_advertisement, args=(context, site, queue))
        proc.start()

    while MP.active_children():
        time.sleep(0.5)

    d = {}
    while not queue.empty():
        (site,ad) = queue.get()
        d[site] = ad

    return d


def delete_sliver_exists(am, context, sname):
    """Attempts to delete all slivers for the given slice at the given AM, suppressing all returned errors."""
    try:
        am.deletesliver(context, sname)
    except DeleteSliverError:
        pass

def _buildaddot(ad, drop_nodes = None):
    """Constructs a dotfile of a topology described by an advertisement rspec.    Only works on very basic GENIv3 advertisements,
    and probably has lots of broken edge cases."""
    # pylint: disable=too-many-branches

    if not drop_nodes:
        drop_nodes = []

    dot_data = []
    dda = dot_data.append # Save a lot of typing

    dda("graph {")

    for node in ad.nodes:
        if node.name in drop_nodes:
            continue

        if node.available:
            dda(f'"{node.name}"')
        else:
            dda(f'"{node.name}" [style=dashed]')

    for link in ad.links:
        if not len(link.interface_refs) == 2:
            print("Link with more than 2 interfaces:")
            print(link.text)

        name_1 = link.interface_refs[0].split(":")[-2].split("+")[-1]
        name_2 = link.interface_refs[1].split(":")[-2].split("+")[-1]

        if name_1 in drop_nodes or name_2 in drop_nodes:
            continue

        dda(f'"{name_1}" -- "{name_2}"')

    dda("}")

    return "\n".join(dot_data)


def builddot(manifests):
    """Constructs a dotfile of the topology described in the passed in manifest list and returns it as a string."""
    # pylint: disable=too-many-branches,import-outside-toplevel
    from .rspec import vtsmanifest as VTSM
    from .rspec.pgmanifest import Manifest as PGM

    dot_data = []
    dda = dot_data.append # Save a lot of typing

    dda("digraph {")

    for manifest in manifests:
        if isinstance(manifest, PGM):
            intf_map = {}
            for node in manifest.nodes:
                dda("\"%s\" [label = \"%s\"]" % (node.sliver_id, node.name))
                for interface in node.interfaces:
                    intf_map[interface.sliver_id] = (node, interface)

            for link in manifest.links:
                label = link.client_id
                name = link.client_id

                if link.vlan:
                    label = "VLAN\n%s" % (link.vlan)
                    name = link.vlan

                dda("\"%s\" [label=\"%s\",shape=doublecircle,fontsize=11.0]" % (name, label))

                for ref in link.interface_refs:
                    dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (
                        intf_map[ref][0].sliver_id, name,
                        intf_map[ref][1].component_id.split(":")[-1]))
                    dda("\"%s\" -> \"%s\"" % (name, intf_map[ref][0].sliver_id))


        elif isinstance(manifest, VTSM.Manifest):
            for dp in manifest.datapaths:
                dda("\"%s\" [shape=rectangle];" % (dp.client_id))

            for ctr in manifest.containers:
                dda("\"%s\" [shape=oval];" % (ctr.client_id))

            dda("subgraph cluster_vf {")
            dda("label = \"SSL VPNs\";")
            dda("rank = same;")
            for vf in manifest.functions:
                if isinstance(vf, VTSM.SSLVPNFunction):
                    dda("\"%s\" [label=\"%s\",shape=hexagon];" % (vf.client_id, vf.note))
            dda("}")

            # TODO: We need to actually go through datapaths and such, but we can approximate for now
            for port in manifest.ports:
                if isinstance(port, VTSM.GREPort):
                    pass
                elif isinstance(port, VTSM.PGLocalPort):
                    dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.shared_vlan,
                                                                                                             port.name))
                    dda("\"%s\" -> \"%s\"" % (port.shared_vlan, port.dpname))
                elif isinstance(port, VTSM.InternalPort):
                    dp = manifest.findTarget(port.dpname)
                    if dp.mirror == port.client_id:
                        continue # The other side will handle it, oddly
                    # TODO: Handle mirroring into another datapath
                    dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.remote_dpname,
                                                                                                             port.name))
                elif isinstance(port, VTSM.InternalContainerPort):
                    # Check to see if the other side is a mirror into us
                    dp = manifest.findTarget(port.remote_dpname)
                    if isinstance(dp, VTSM.ManifestDatapath):
                        if port.remote_client_id == dp.mirror:
                            remote_port_name = port.remote_client_id.split(":")[-1]
                            dda("\"%s\" -> \"%s\" [headlabel=\"%s\",taillabel=\"%s\",style=dashed]" % (
                                    port.remote_dpname, port.dpname, port.name, remote_port_name))
                            continue

                    # No mirror, draw as normal
                    dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.remote_dpname,
                                                                                                             port.name))
                elif isinstance(port, VTSM.VFPort):
                    dda("\"%s\" -> \"%s\"" % (port.dpname, port.remote_client_id))
                    dda("\"%s\" -> \"%s\"" % (port.remote_client_id, port.dpname))

                elif isinstance(port, VTSM.GenericPort):
                    pass
                else:
                    continue ### TODO: Unsupported Port Type


    dda("}")

    return "\n".join(dot_data)


class APIEncoder(json.JSONEncoder):
    def default(self, obj): # pylint: disable=E0202
        if hasattr(obj, "__json__"):
            return obj.__json__()
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def loa_aggregates(path = None):
    if not path:
        path = GCU.getDefaultAggregatePath()

    ammap = {}
    try:
        obj = json.loads(open(path, "r").read())
        for aminfo in obj["specs"]:
            ams = AMSpec._jconstruct(aminfo)
            am = ams.build()
            if am:
                ammap[am.name] = am
    except IOError:
        pass

    return ammap

def update_aggregates(context, ammap):
    from .aggregate.core import load_from_registry

    new_map = load_from_registry(context)
    for key, val in new_map.items():
        if key not in ammap:
            ammap[key] = val
    save_aggregates(ammap)

def save_aggregates(ammap, path = None):
    if not path:
        path = GCU.getDefaultAggregatePath()

    obj = {"specs" : [x._amspec for x in ammap.values() if x._amspec]}
    with open(path, "w+") as f:
        data = json.dumps(obj, cls=APIEncoder)
        f.write(data)


def load_context(path = None, key_passphrase = None):
    from geni.aggregate import FrameworkRegistry
    from geni.aggregate.context import Context
    from geni.aggregate.user import User

    if path is None:
        path = GCU.getDefaultContextPath()
    else:
        path = os.path.expanduser(path)

    with open(path, "r") as file:
        obj = json.load(file)

    version = _getdefault(obj, "version", 1)

    if key_passphrase is True:
        key_passphrase = getpass.getpass("Private key passphrase: ")

    if version == 1:
        if "framework" in obj:
            cfile = FrameworkRegistry.get(obj["framework"])()
        else:
            raise RuntimeError("json file is missing field `framework`")

        cfile.cert = obj["cert-path"]
        if key_passphrase:
            if six.PY3:
                key_passphrase = bytes(key_passphrase, "utf-8")
            cfile.setKey(obj["key-path"], key_passphrase)
        else:
            cfile.key = obj["key-path"]

        user = User()
        user.name = obj["user-name"]
        user.urn = obj["user-urn"]
        user.add_key(obj["user-pubkeypath"])

        context = Context()
        context.add_user(user)
        context.cf = cfile
        context.project = obj["project"]
        context.path = path

    elif version == 2:
        context = Context()

        fobj = obj["framework-info"]
        cfile = FrameworkRegistry.get(fobj["type"])()
        cfile.cert = fobj["cert-path"]
        if key_passphrase:
            cfile.setKey(fobj["key-path"], key_passphrase)
        else:
            cfile.key = fobj["key-path"]
        context.cf = cfile
        context.project = fobj["project"]
        context.path = path

        ulist = obj["users"]
        for uobj in ulist:
            user = User()
            user.name = uobj["username"]
            user.urn = _getdefault(uobj, "urn", None)
            klist = uobj["keys"]
            for keypath in klist:
                user.add_key(keypath)
            context.add_user(user)

    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    cert = x509.load_pem_x509_certificate(open(context._cf.cert, "rb").read(), default_backend())
    if cert.not_valid_after < datetime.datetime.now():
        print("***WARNING*** Client SSL certificate supplied in this context is expired")
    return context


def hasDataContext():
    path = GCU.getDefaultContextPath()
    return os.path.exists(path)


class MissingPublicKeyError(Exception):
    def __str__ (self):
        return "Your bundle does not appear to contain an SSH public key.    You must supply a path to one."


class PathNotFoundError(Exception):
    def __init__ (self, path):
        super().__init__()
        self._path = path

    def __str__ (self):
        return "The path %s does not exist." % (self._path)

def _find_ssh_keygen ():
    PATHS = ["/usr/bin/ssh-keygen", "/bin/ssh-keygen", "/usr/sbin/ssh-keygen", "/sbin/ssh-keygen"]
    for path in PATHS:
        if os.path.exists(path):
            return path

MAKE_KEYPAIR = (-1, 1)

def buildContextFromBundle(bundle_path, pubkey_path = None, cert_pkey_path = None):
    HOME = os.path.expanduser("~")

    # Create the .bssw directories if they don't exist
    DEF_DIR = GCU.getDefaultDir()

    zfile = zipfile.ZipFile(os.path.expanduser(bundle_path))

    zip_pubkey_path = None
    if pubkey_path is None or pubkey_path == MAKE_KEYPAIR:
        # search for pubkey-like file in zip
        for fname in zfile.namelist():
            if fname.startswith("ssh/public/") and fname.endswith(".pub"):
                zip_pubkey_path = fname
                break

        if not zip_pubkey_path and pubkey_path != MAKE_KEYPAIR:
            raise MissingPublicKeyError()

    # Get URN/Project/username from omni_config
    urn = None
    project = None

    oc = zfile.open("omni_config")
    for line in oc.readlines():
        if line.startswith("urn"):
            urn = line.split("=")[1].strip()
        elif line.startswith("default_project"):
            project = line.split("=")[1].strip()

    uname = urn.rsplit("+")[-1]

    # Create .ssh if it doesn't exist
    try:
        os.makedirs("%s/.ssh" % (HOME), 0o775)
    except OSError:
        pass

    # If a pubkey wasn't supplied on the command line, we may need to install both keys from the bundle
    # This will catch if creation was requested but failed
    pkpath = pubkey_path
    if not pkpath or pkpath == MAKE_KEYPAIR:
        found_private = False

        if "ssh/private/id_geni_ssh_rsa" in zfile.namelist():
            found_private = True
            if not os.path.exists("%s/.ssh/id_geni_ssh_rsa" % (HOME)):
                # If your umask isn't already 0, we can't safely create this file with the right permissions
                with os.fdopen(os.open("%s/.ssh/id_geni_ssh_rsa" % (HOME), os.O_WRONLY | os.O_CREAT, 0o600), "w") as tfile:
                    tfile.write(zfile.open("ssh/private/id_geni_ssh_rsa").read())

        if zip_pubkey_path:
            pkpath = "%s/.ssh/%s" % (HOME, zip_pubkey_path[len('ssh/public/'):])
            if not os.path.exists(pkpath):
                with open(pkpath, "w+") as tfile:
                    tfile.write(zfile.open(zip_pubkey_path).read())

        # If we don't find a proper keypair, we'll make you one if you asked for it
        # This preserves your old pubkey if it existed in case you want to use that later
        if not found_private and pubkey_path == MAKE_KEYPAIR:
            keygen = _find_ssh_keygen()
            subprocess.call("%s -t rsa -b 2048 -f ~/.ssh/genilib_rsa -N ''" % (keygen), shell = True)
            pkpath = os.path.expanduser("~/.ssh/genilib_rsa.pub")
    else:
        pkpath = os.path.expanduser(pubkey_path)
        if not os.path.exists(pkpath):
            raise PathNotFoundError(pkpath)

    # We write the pem into 'private' space
    zfile.extract("geni_cert.pem", DEF_DIR)

    if cert_pkey_path is None:
        ckpath = f"{DEF_DIR}/geni_cert.pem"
    else:
        # Use user-provided key path instead of key inside .pem
        ckpath = os.path.expanduser(cert_pkey_path)
        if not os.path.exists(ckpath):
            raise PathNotFoundError(ckpath)

    cdata = {}
    cdata["framework"] = "portal"
    cdata["cert-path"] = f"{DEF_DIR}/geni_cert.pem"
    cdata["key-path"] = ckpath
    cdata["user-name"] = uname
    cdata["user-urn"] = urn
    cdata["user-pubkeypath"] = pkpath
    cdata["project"] = project

    with open(f"{DEF_DIR}/context.json", "w+", encoding='utf-8') as jfile:
        json.dump(cdata, jfile)

def _build_context(framework, cert_path, key_path, username, user_urn, pubkey_path, project, path=None):
    # Create the .bssw directories if they don't exist
    default_dir = GCU.getDefaultDir()

    new_cert_path = "%s/%s" % (default_dir, os.path.basename(cert_path))

    try:
        shutil.copyfile(cert_path, new_cert_path)
        LOG.info("Installed certificate file at '%s'", new_cert_path)
    except shutil.SameFileError:
        pass # File already was where it was supposed to go

    if key_path != cert_path:
        new_key_path = "%s/%s" % (default_dir, os.path.basename(key_path))
        shutil.copyfile(key_path, new_key_path)
    else:
        new_key_path = new_cert_path

    if not path:
        path = f"{default_dir}/context.json"

    cdata = {}
    cdata["framework"] = framework
    cdata["cert-path"] = new_cert_path
    cdata["key-path"] = new_key_path
    cdata["user-name"] = username
    cdata["user-urn"] = user_urn
    cdata["user-pubkeypath"] = pubkey_path
    cdata["project"] = project

    with open(path, "w+", encoding="utf-8") as jfile:
        json.dump(cdata, jfile)
