# pylint: disable=missing-class-docstring
import os
import platform
import shutil
from pathlib import Path
import urllib
import sys
from distutils.util import get_platform
from distutils.command.build import build as st_build

from setuptools import setup
from setuptools.command.develop import develop as st_develop


def _download_joern():
    pass 


class build(st_build):
    def run(self, *args):
        self.execute(_download_joern, (), msg="Copying models from shared link...")
        super().run(*args)


class develop(st_develop):
    def run(self, *args):
        self.execute(_download_joern, (), msg="Copying models from shared link...")
        super().run(*args)


cmdclass = {
    "build": build,
    "develop": develop,
}

if 'bdist_wheel' in sys.argv and '--plat-name' not in sys.argv:
    sys.argv.append('--plat-name')
    name = get_platform()
    if 'linux' in name:
        sys.argv.append('manylinux2014_' + platform.machine())
    else:
        # https://www.python.org/dev/peps/pep-0425/
        sys.argv.append(name.replace('.', '_').replace('-', '_'))

setup()
