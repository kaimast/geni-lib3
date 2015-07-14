# Copyright (c) 2014  Barnstormer Softworks, Ltd.

from distutils.core import setup
import setuptools

setup(name = 'geni-lib',
      version = '1.1',
      author = 'Nick Bastin',
      author_email = 'nick@bssoftworks.com',
      packages = setuptools.find_packages(),
      scripts = ['tools/buildcontext/context-from-bundle',
                 'tools/shell/genish'],
      )
