import subprocess
import os


class SystemChecker:
    @staticmethod
    def is_nfnetlink_queue_available() -> bool:
        try:
            if os.path.isdir("/sys/module/nfnetlink_queue"):
                return True

            subprocess.check_output(["lsmod"], stderr=subprocess.STDOUT)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            if os.path.exists("/proc/modules"):
                with open("/proc/modules") as f:
                    if "nfnetlink_queue" in f.read():
                        return True
        return False

    @staticmethod
    def has_sudo_permissions() -> bool:
        try:
            subprocess.run(
                ['sudo', '-n', 'iptables', '-L'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
