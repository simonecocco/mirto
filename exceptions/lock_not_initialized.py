class LockNotInitialized(Exception):
    def __init__(self, lock_name):
        self._lock_name = lock_name
        super().__init__(f'{lock_name} is not initialized')

    @property
    def lock_name(self):
        return self._lock_name
