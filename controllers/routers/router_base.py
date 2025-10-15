from abc import abstractmethod, ABC
from utils.process_orchestrator import ProcessOrchestrator


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
