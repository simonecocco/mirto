from multiprocessing import Process, Manager
from exceptions.process_not_exists import ProcessNotExists


class ProcessOrchestrator:
    def __init__(self, process_synchronizer, user_prefs, logger):
        self._process_synchronizer = process_synchronizer
        self._processes = {}
        self._shared_data = Manager.dict()
        self._logger = logger
        self._user_prefs = user_prefs

    @property
    def get_user_prefs(self):
        return self._user_prefs

    @property
    def get_logger(self):
        return self._logger

    @property
    def get_process_synchronizer(self):
        return self._process_synchronizer

    @property
    def get_shared_data(self):
        return self._shared_data

    def new_process(self, name, function):
        self._processes[name] = Process(
            target=function,
            args=(self)
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
