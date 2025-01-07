__version__ = "4.0.150.1"

import hashlib
import os
from pathlib import Path
import importlib.resources
import subprocess
import urllib.request
import math

from tqdm import tqdm

# initialize logging for the entire project
import logging
logging.getLogger("pyjoern").addHandler(logging.NullHandler())
from .logger import Loggers
loggers = Loggers()
del Loggers

_l = logging.getLogger(__name__)

JOERN_VERSION = "v4.0.150"
JOERN_BIN_DIR_PATH = Path(Path(str(importlib.resources.files("pyjoern"))) / "bin/joern-cli").absolute()
JOERN_SERVER_PATH = JOERN_BIN_DIR_PATH / "joern"
JOERN_EXPORT_PATH = JOERN_BIN_DIR_PATH / "joern-export"
JOERN_PARSE_PATH = JOERN_BIN_DIR_PATH / "joern-parse"
# must update both of these on supported Joern backend update
JOERN_ZIP_HASH = "07b806e2e5bc4fc291e75c9dbdd1aea9658632f08564788116e3d11611dc1001a252ffef8413e296c9f4d457970afc2a183276c7fa5c82dc5ae87810cbf829f5"
# must be imported after defining project wide constants
from .client import JoernClient
from .server import JoernServer
from .cfg import fast_cfgs_from_source
from .parsing import parse_source


#
# Helper code for downloading Joern server backend
#

def _download_and_save_joern_zip(save_location: Path, verify=True) -> Path:
    # XXX: hacked code for non-ssl verification
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    url = f"https://github.com/joernio/joern/releases/download/{JOERN_VERSION}/joern-cli.zip"
    with urllib.request.urlopen(url) as response:
        total_size = response.length
        if response.status != 200:
            raise Exception(f"HTTP error {response.status}: {response.reason}")

        hasher = hashlib.sha512()
        chunk_size = 8192
        mb_size = int(total_size / 1000000)
        with open(save_location, 'wb') as f:
            for _ in tqdm(range(math.ceil(total_size / chunk_size)), desc=f"Downloading Joern bytes (~{mb_size} MB)..."):
                chunk = response.read(chunk_size)
                hasher.update(chunk)
                if not chunk:
                    break

                f.write(chunk)

        # hash for extra security
        download_hash = hasher.hexdigest()
        if verify and download_hash != JOERN_ZIP_HASH:
            raise Exception(f"Joern files corrupted in download: {download_hash} != {JOERN_ZIP_HASH}")

    return save_location


def _download_joern():
    joern_binary = JOERN_BIN_DIR_PATH / "joern"
    if joern_binary.exists():
        return

    # download joern
    if not JOERN_BIN_DIR_PATH.parent.exists():
        os.mkdir(JOERN_BIN_DIR_PATH.parent)
    joern_zip_file = _download_and_save_joern_zip(JOERN_BIN_DIR_PATH.parent / "joern-cli.zip", verify=True)
    # unzip joern
    subprocess.run(["unzip", str(joern_zip_file)], cwd=str(JOERN_BIN_DIR_PATH.parent), capture_output=True, check=True)
    # remove zip file
    joern_zip_file.unlink()

    if not joern_binary.exists():
        raise Exception("Failed to download Joern!")


if not JOERN_BIN_DIR_PATH.exists():
    _l.info(f"Joern binaries are not installed on your system, downloading them now...")
    _download_joern()
    if not JOERN_BIN_DIR_PATH.exists():
        raise Exception("Failed to download Joern on startup!")
