# pylint: disable=missing-class-docstring
import platform
import urllib.request
from pathlib import Path
import sys
from distutils.util import get_platform
from distutils.command.build import build as st_build
from subprocess import run
import hashlib

from setuptools import setup
from setuptools.command.develop import develop as st_develop

# must update both of these on supported Joern backend update
JOERN_VERSION = "v1.2.18"
JOERN_ZIP_HASH = "58ef92c407d6ec4af02b1185bd481562"


def _download_joern_zipfile(save_location: Path) -> Path:
    # XXX: hacked code for non-ssl verification
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    url = f"https://github.com/joernio/joern/releases/download/{JOERN_VERSION}/joern-cli.zip"
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise Exception(f"HTTP error {response.status}: {response.reason}")

        hasher = hashlib.md5()
        with open(save_location, 'wb') as f:
            while True:
                chunk = response.read(8192)
                hasher.update(chunk)
                if not chunk:
                    break

                f.write(chunk)

        # hash for extra security
        download_hash = hasher.hexdigest()
        if download_hash != JOERN_ZIP_HASH:
            raise Exception(f"Joern files corrupted in download: {download_hash} != {JOERN_ZIP_HASH}")

    return save_location


def _download_joern():
    joern_bin_dir = Path("pyjoern/bin").absolute()
    joern_binary = joern_bin_dir / "joern-cli" / "joern"
    #if joern_binary.exists():
    #    return
    with open("/home/runner/work/pyjoern/we_made_it_to_validation.txt", "w") as fp:
        fp.write(f"{joern_binary}")

    # download joern
    joern_zip_file = _download_joern_zipfile(joern_bin_dir / "joern-cli.zip")
    # unzip joern
    run(["unzip", str(joern_zip_file)], cwd=str(joern_bin_dir))
    # remove zip file
    joern_zip_file.unlink()

    if not joern_binary.exists():
        raise Exception("Failed to download Joern!")




class build(st_build):
    def run(self, *args):
        self.execute(_download_joern, (), msg="Downloading Joern from GitHub...")
        super().run(*args)


class develop(st_develop):
    def run(self, *args):
        self.execute(_download_joern, (), msg="Downloading Joern from GitHub...")
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

setup(cmdclass=cmdclass)
