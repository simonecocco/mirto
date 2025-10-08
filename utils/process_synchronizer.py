from multiprocessing import Lock
from mirto.exceptions.lock_not_initialized import LockNotInitialized


class ProcessSynchronizer:
    MAIN_LOCK = 'PROCESS_SYNCHRONIZER_MAIN_LOCK'

    def __init__(self):
        self._locks_dict = {}
        self._processes = {}
        self.create_lock(ProcessSynchronizer.MAIN_LOCK)

    def create_lock(self, name):
        self._locks_dict[name] = Lock()

    @property
    def main_lock(self):
        return self.get_lock(ProcessSynchronizer.MAIN_LOCK)

    def get_lock(self, name):
        if name not in self._locks_dict:
            raise LockNotInitialized(name)
