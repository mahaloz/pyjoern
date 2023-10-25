__version__ = "1.2.18.1"

from pathlib import Path
import logging

_l = logging.getLogger(__name__)

JOERN_BIN_DIR_PATH = Path(Path(__file__).parent / "bin" / "joern-cli").absolute()
JOERN_SERVER_PATH = JOERN_BIN_DIR_PATH / "joern"
JOERN_EXPORT_PATH = JOERN_BIN_DIR_PATH / "joern-export"
JOERN_PARSE_PATH = JOERN_BIN_DIR_PATH / "joern-parse"

if not JOERN_BIN_DIR_PATH.exists():
    raise FileNotFoundError(f"Joern bin directory not found at {JOERN_BIN_DIR_PATH}, please reinstall!")

from .client import JoernClient
from .server import JoernServer
from .cfg import fast_cfgs_from_source

