import subprocess
from time import time, sleep
import os
import logging

from cpgqls_client import CPGQLSClient
from .client import JoernClient

import psutil

l = logging.getLogger(__name__)


class JoernServer:
    def __init__(self, ip="localhost", port=9000):
        self.ip = ip
        self.port = port

    def __enter__(self):
        self.start()
        self.wait_for_server_start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()

    def start(self):
        # always kill proc of the same port before starting
        joern_proc = self._find_joern_proc()
        if joern_proc:
            joern_proc.kill()

        proc = subprocess.Popen([f'joern --server --server-port {self.port} >> /tmp/t.tmp 2>&1 &'], shell=True)
        return True

    def wait_for_server_start(self, timeout=20):
        start_time = time()
        success = False
        while time() - start_time < timeout:
            if self._find_joern_proc():
                try:
                    CPGQLSClient(f"{self.ip}:{self.port}").execute("val a = 1")
                except ConnectionRefusedError:
                    pass
                else:
                    success = True
                    break

            sleep(0.5)

        if not success:
            l.critical(f"Was unable to start the JOERN server on port {self.port} before timeout...")

    def stop(self):
        joern_proc = self._find_joern_proc()
        if joern_proc:
            joern_proc.kill()
        else:
            l.critical(f"Unable to kill the Joern server on port {self.port} because it's dead our changed id")

        try:
            os.unlink("t.tmp")
        except Exception:
            pass

    def reboot(self):
        self.stop()
        self.start()
        self.wait_for_server_start()

    def _find_joern_proc(self):
        for proc in psutil.process_iter():
            try:
                cmd = " ".join(proc.cmdline())
            except Exception as e:
                continue

            if "java" in cmd and "joern" in cmd and f"--server-port {self.port}" in cmd:
                break
        else:
            proc = None

        return proc

