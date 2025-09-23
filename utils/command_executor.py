from subprocess import run as run_cmd


class CommandExecutor:
    def __call__(self, command):
        self.execute(command)

    def execute(self, command):
        run_cmd(command)
