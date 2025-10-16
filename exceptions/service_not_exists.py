class ServiceNotExists(Exception):
    def __init__(self, port):
        super().__init__(f'service at {port} not exists')
