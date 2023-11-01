import shutil
import signal
from typing import Union
import os
import subprocess
import typing
from pathlib import Path
import platform


class WorkDirContext:
    def __init__(self, path: Union[Path, str]):
        self.path = Path(path)
        self.origin = Path(os.getcwd()).absolute()

    def __enter__(self):
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.origin)


class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type_, value, traceback):
        signal.alarm(0)


class PackageInstaller:
    OS_LINUX = 'linux'
    OS_MAC = 'mac'
    OS_WINDOWS = 'windows'
    OS_UNK = 'unknown'

    def __init__(self, package_names=None):
        self.os = self.discover_os()
        if package_names is not None:
            self.install_system_packages(package_names)

    def install_system_packages(self, package_names: typing.List[str], update_first=True):
        if self.os == self.OS_LINUX:
            self.install_linux_packages(package_names, update_first=update_first)
        elif self.os == self.OS_MAC:
            self.install_mac_packages(package_names, update_first=update_first)
        elif self.os == self.OS_WINDOWS:
            raise NotImplementedError()
        else:
            raise Exception('Unknown OS')

    def install_linux_packages(self, package_names: typing.List[str], update_first=True):
        installer = "apt"
        self.installer_is_installed(installer)

        if not self.user_is_root():
            installer = "sudo " + installer

        if update_first:
            self.run_command(f"{installer} update -y")

        packages = " ".join(package_names)
        stdout = self.run_command(f"{installer} install -y {packages}")
        if stdout is None:
            print(f"Failed to install packages: {packages}")

    def install_mac_packages(self, package_names: typing.List[str], update_first=True):
        installer = "brew"
        self.installer_is_installed(installer)

        if update_first:
            self.run_command(f"{installer} update")

        packages = " ".join(package_names)
        stdout = self.run_command(f"{installer} install {packages}")
        if stdout is None:
            print(f"Failed to install packages: {packages}")

    #
    # Unix Utils
    #

    @staticmethod
    def user_is_root():
        return os.getuid() == 0

    @staticmethod
    def discover_os():
        if platform.system() == 'Linux':
            return PackageInstaller.OS_LINUX
        elif platform.system() == 'Darwin':
            return PackageInstaller.OS_MAC
        elif platform.system() == 'Windows':
            return PackageInstaller.OS_WINDOWS
        else:
            return PackageInstaller.OS_UNK

    def command_is_installed(self, package_name: str):
        if self.os not in [self.OS_LINUX, self.OS_MAC]:
            raise NotImplementedError()

        stdout = self.run_command(f"which {package_name}")
        if not stdout:
            return False

        return True

    def installer_is_installed(self, installer: str):
        if self.os not in [self.OS_LINUX, self.OS_MAC]:
            raise NotImplementedError()

        # sanity check installer
        if not self.command_is_installed(installer):
            raise Exception(f"Installer '{installer}' is not installed. Please install it.")


    @staticmethod
    def run_command(command: str, as_shell=False, normalize_cmd=True, is_root=None) -> typing.Optional[str]:
        """
        Runs a command in the system. Returns either the stdout or None if it failed.

        :param command:
        :param as_shell:
        :param normalize_cmd:  Normalize the command before running it. This is useful for commands that use ~ or $.
        :return:
        """
        if normalize_cmd:
            shell_strs = ["&&", "||", ">", "<", "|", ";", "&", "*", "$"]
            if any([s in command for s in shell_strs]):
                as_shell = True

            if "~" in command:
                # XXX: if a space is in this, it will break
                command = command.replace("~", str(Path.home()))

            is_root = is_root or PackageInstaller.user_is_root()
            if is_root and "sudo" in command:
                command = command.replace("sudo ", "")

        cmd_list = command.split(' ') if not as_shell else command
        try:
            out = subprocess.run(cmd_list, shell=as_shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            text = out.stdout.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            text = None

        return text
