import argparse
import logging

_l = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="The command line tool for PyJoern. Do things like initializing Joern and running queries."
    )
    parser.add_argument(
        "--install", action="store_true", help="Install Joern backend and dependencies."
    )
    args = parser.parse_args()

    if args.install:
        # side effect: checks Joern backend is installed and copies it down otherwise
        from pyjoern.utils import PackageInstaller
        # dependencies:
        # graphviz-dev, unzip, openjdk-19-jdk
        packages = ["graphviz-dev", "unzip"]
        installer = PackageInstaller()
        if installer.os == installer.OS_LINUX:
            packages += ["openjdk-19-jdk"]
        elif installer.os == installer.OS_MAC:
            packages += ["openjdk@19"]
        else:
            raise Exception("Unknown OS, please install the dependencies manually.")

        _l.info("PyJoern successfully installed!")


if __name__ == "__main__":
    main()
