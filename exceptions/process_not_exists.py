class ProcessNotExists(Exception):
    def __init__(self, process_name):
        self._process_name = process_name
        super().__init__(f'The process {process_name} not exists')

    @property
    def process_name(self):
        return self._process_name
