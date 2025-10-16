class DuplicateServicePort(Exception):
    def __init__(self, port):
        super().__init__(f'A service exists already in port {port}')
