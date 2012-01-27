#!/usr/bin/env python

from distutils.core import setup
import sys

sys.path.append("atomize")
import atomize

setup(name="atomize",
      version="%s.%s.%s" % atomize.__version__,
      author="Christopher Wienberg, John Garland",
      author_email="cwienberg@ict.usc.edu, johnnybg@gmail.com",
      url="https://github.com/johnnyg/atomize",
      download_url="https://github.com/johnnyg/atomize/downloads",
      description="A simple Python package for easily generating Atom feeds",
      long_description="A pure-Python package for easily generating Atom Syndicated Format feeds.",
      package_dir={"": "atomize"},
      py_modules=["atomize"],
      provides=["atomize"],
      keywords="atom web",
      license="Eclipse Public License 1.0")
