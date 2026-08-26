__version__ = "4.0.612.0"

import hashlib
import os
from pathlib import Path
import platform
import shutil
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

JOERN_VERSION = "v4.0.612"
# Joern's native frontends (rust2cpg and friends) locate their astgen helper by walking up from their
# own jar for as long as the whole path still contains "lib", so an install under site-packages sends
# them looking in the Python prefix instead. The backend therefore lives outside the package.
JOERN_DIR_ENV_VAR = "PYJOERN_JOERN_DIR"
JOERN_BIN_DIR_PATH = Path(os.environ.get(JOERN_DIR_ENV_VAR) or Path.home() / ".pyjoern").absolute() / "joern-cli"
JOERN_SERVER_PATH = JOERN_BIN_DIR_PATH / "joern"
JOERN_EXPORT_PATH = JOERN_BIN_DIR_PATH / "joern-export"
JOERN_PARSE_PATH = JOERN_BIN_DIR_PATH / "joern-parse"
# Joern ships a platform-specific release zip (native frontends like rust2cpg are compiled per-platform).
# Both the version above and every hash below must be updated on a supported Joern backend update. The
# hashes are the ones published as `<zip_name>.sha512` next to each release asset.
JOERN_ZIP_HASHES = {
    "joern-cli-linux-arm64.zip": "c5d26914a13c8fa08b354e0efd66e49160882345906ec01f90727213232b2668f456dc632a2390c04f3b01c87aaf5433b08ce174e022fca6a2d91bb6796fb4c1",
    "joern-cli-linux-x86_64.zip": "9150546302bcb020aab8a4e7efc9c3b9ca37d5679f0316066cbe332f3628f33c41658a7c8b686c2ff13f7c29ead3881627ef01701dca74e1b1ad0d1018e922a8",
    "joern-cli-macos-arm64.zip": "ad3c920469448db672f1fa71cbd9cbe7d4d79c4093415bb38139cc71b3048175eb3cad64e90e6672aacfa82f2d2d48e2ca121977c602069d20889e9a25feb1d3",
    "joern-cli-macos-x86_64.zip": "ca5f71b177835c21d8d150524757571cffd38fd210261cfb84e4ce1f4805a063ad062d072ed08bea1ca89f9bd5a45a757fb2bfb274b18ad8718ad37eec6f1288",
    "joern-cli-windows-arm64.zip": "c1ae4d6d8686f4786a617f101c36053ed0ea4e671b82fd90779dc45ae7278fb8d086c1c4229de4039086b2cb840100abefa8c5b3085e24d41145d9b1c912bb63",
    "joern-cli-windows-x86_64.zip": "46b7c80055b959c468240a1e57e2fb23a1aa90f0f8b0336ab4676ea58654e7be0bec3e7b09a6266a8c2aafc28d501978e33c208b9c69095dca540a062e31d320",
}

_OS_NAMES = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}
_ARCH_NAMES = {
    "arm64": "arm64", "aarch64": "arm64",
    "x86_64": "x86_64", "amd64": "x86_64", "AMD64": "x86_64",
}


def joern_zip_name() -> str:
    """
    The name of the Joern release asset matching the current platform, e.g. `joern-cli-macos-arm64.zip`.
    """
    system = platform.system()
    machine = platform.machine()
    os_name = _OS_NAMES.get(system)
    arch_name = _ARCH_NAMES.get(machine)
    if os_name is None or arch_name is None:
        raise Exception(
            f"Joern {JOERN_VERSION} publishes no release for this platform ({system} {machine}). "
            f"Supported platforms: {sorted(JOERN_ZIP_HASHES)}"
        )

    zip_name = f"joern-cli-{os_name}-{arch_name}.zip"
    if zip_name not in JOERN_ZIP_HASHES:
        raise Exception(f"No known Joern release asset {zip_name} for Joern {JOERN_VERSION}")

    return zip_name

# must be imported after defining project wide constants
from .client import JoernClient
from .server import JoernServer
from .cfg import fast_cfgs_from_source
from .parsing import parse_source, parse_callgraph


#
# Helper code for downloading Joern server backend
#

def _download_and_save_joern_zip(save_location: Path, verify=True) -> Path:
    # XXX: hacked code for non-ssl verification
    import ssl

    ssl._create_default_https_context = ssl._create_unverified_context

    zip_name = joern_zip_name()
    url = f"https://github.com/joernio/joern/releases/download/{JOERN_VERSION}/{zip_name}"
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
        expected_hash = JOERN_ZIP_HASHES[zip_name]
        if verify and download_hash != expected_hash:
            raise Exception(f"Joern files corrupted in download: {download_hash} != {expected_hash}")

    return save_location


def _warn_on_unresolvable_astgen_dir():
    """
    Warns when the install path defeats how Joern locates the astgen helpers its native frontends need.

    Joern walks up from a frontend jar while the path still contains "lib", so it lands on the wrong
    directory whenever any ancestor of the install has "lib" in its name.
    """
    if "lib" in str(JOERN_BIN_DIR_PATH):
        _l.warning(
            f"Joern is installed under {JOERN_BIN_DIR_PATH}, which contains 'lib'. Joern's native "
            f"frontends (Rust among them) will look for their astgen helpers in the wrong directory. "
            f"Set ${JOERN_DIR_ENV_VAR} to a path without 'lib' in it to parse those languages."
        )


def installed_joern_version() -> str | None:
    """
    The version of the Joern backend currently installed on this system, or None when there is none.
    """
    jar_prefix, jar_suffix = "io.joern.joern-cli-", ".jar"
    for jar in (JOERN_BIN_DIR_PATH / "lib").glob(f"{jar_prefix}*{jar_suffix}"):
        return "v" + jar.name[len(jar_prefix):-len(jar_suffix)]

    return None


def _download_joern():
    joern_binary = JOERN_BIN_DIR_PATH / "joern"
    if joern_binary.exists():
        return

    # download joern
    JOERN_BIN_DIR_PATH.parent.mkdir(parents=True, exist_ok=True)
    joern_zip_file = _download_and_save_joern_zip(JOERN_BIN_DIR_PATH.parent / joern_zip_name(), verify=True)
    # unzip joern
    subprocess.run(["unzip", str(joern_zip_file)], cwd=str(JOERN_BIN_DIR_PATH.parent), capture_output=True, check=True)
    # remove zip file
    joern_zip_file.unlink()

    if not joern_binary.exists():
        raise Exception("Failed to download Joern!")


_warn_on_unresolvable_astgen_dir()
_installed_version = installed_joern_version()
if _installed_version != JOERN_VERSION:
    if _installed_version is None:
        _l.info(f"Joern binaries are not installed on your system, downloading them now...")
    else:
        # PyJoern parses the graphs Joern exports, and that format changes between Joern releases, so an
        # unsupported backend has to go rather than be parsed with the wrong expectations.
        _l.info(
            f"Installed Joern {_installed_version} is not the backend PyJoern supports ({JOERN_VERSION}), "
            f"replacing it now..."
        )
        shutil.rmtree(JOERN_BIN_DIR_PATH)

    _download_joern()
    _installed_version = installed_joern_version()
    if _installed_version != JOERN_VERSION:
        raise Exception(f"Failed to install Joern {JOERN_VERSION} on startup, got {_installed_version}!")
