from multiprocessing import Process, Manager
from exceptions.process_not_exists import ProcessNotExists
from user.user_preferences import UserPreferences
from logging import Logger


class ProcessOrchestrator:
    def __init__(self, process_synchronizer, user_prefs, logger):
        self._process_synchronizer = process_synchronizer
        self._processes = {}
        self._manager = Manager()
        self._shared_data = self._manager.dict()
        self._logger: Logger = logger
        self._user_prefs = user_prefs

    def get_user_prefs(self) -> UserPreferences:
        return self._user_prefs

    def get_logger(self) -> Logger:
        return self._logger

    def get_process_synchronizer(self):
        return self._process_synchronizer

    def get_shared_data(self):
        return self._shared_data

    def new_process(self, name, function):
        self._processes[name] = Process(
            target=function,
            args=(self,)
        )
        self._processes[name].start()

    def __delitem__(self, key):
        if key not in self._processes:
            raise ProcessNotExists(key)

        self._processes[key].terminate()
        self._processes[key].join()

    def __del__(self):
        for process_name in self._processes:
            del self[process_name]
