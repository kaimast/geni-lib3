# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

from distutils.core import setup
import setuptools

import os
import os.path

# If you are on linux, and don't have ca-certs, we can do an awful thing and it will still work
if os.name == "posix" and os.uname()[0] == "Linux" and not os.path.exists("/etc/ssl/certs/ca-certificates.crt"):
  import ssl
  ssl._create_default_https_context = ssl._create_unverified_context

setup(name = 'geni-lib',
      version = '0.9',
      author = 'Nick Bastin',
      author_email = 'nick@bssoftworks.com',
      packages = setuptools.find_packages(),
      scripts = ['tools/buildcontext/context-from-bundle',
                 'tools/shell/genish'],
      install_requires = [
        "requests >= 2.7.0",
        "cryptography",
        ]
      )
