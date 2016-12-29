# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages

import os
import os.path

# If you are on linux, and don't have ca-certs, we can do an awful thing and it will still work
if os.name == "posix" and os.uname()[0] == "Linux" and not os.path.exists("/etc/ssl/certs/ca-certificates.crt"):
  import ssl
  ssl._create_default_https_context = ssl._create_unverified_context

setup(name = 'geni-lib',
      version = '0.9.3',
      author = 'Nick Bastin',
      author_email = 'nick@bssoftworks.com',
      packages = find_packages(),
      scripts = ['tools/buildcontext/context-from-bundle',
                 'tools/shell/genish'],
      install_requires = [
        "cryptography==1.6",
        "wrapt",
        ],
      classifiers = [
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        ]
      )
