from abc import ABC, abstractmethod
from utils.process_orchestrator import ProcessOrchestrator


class BasePacketCapturer(ABC):
    def __init__(self, process_orchestrator: ProcessOrchestrator):
        self._process_orchestrator: ProcessOrchestrator = process_orchestrator

    @property
    def orchestrator(self) -> ProcessOrchestrator:
        return self._process_orchestrator

    @abstractmethod
    def each_packet(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self):
        pass
