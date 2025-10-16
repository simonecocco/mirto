from abc import abstractmethod, ABC
from utils.process_orchestrator import ProcessOrchestrator
from flask import Response

GENERIC_ERROR_MESSAGE = 'See console log'


class RouterBase(ABC):
    def __init__(self, name: str, process_orchestrator: ProcessOrchestrator) -> None:
        self._api_name: str = name
        self._process_orchestrator: ProcessOrchestrator = process_orchestrator

    def get_process_orchestrator(self) -> ProcessOrchestrator:
        return self._process_orchestrator

    @property
    def name(self) -> str:
        return self._api_name

    @abstractmethod
    def _configure_auth(self) -> None:
        pass

    def client_fail(self, err, msg=GENERIC_ERROR_MESSAGE, status=400):
        self._process_orchestrator.get_logger().error(err)
        return Response(msg, status=status)

    def server_fail(self, err, msg=GENERIC_ERROR_MESSAGE, status=500):
        self._process_orchestrator.get_logger().error(err)
        return Response(msg, status=status)

    @property
    def OK(self):
        return Response('OK', status=200)
