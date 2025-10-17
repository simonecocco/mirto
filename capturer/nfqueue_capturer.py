from utils.process_orchestrator import ProcessOrchestrator
from capturer.base_capturer import BasePacketCapturer


class NFQueueCapturer(BasePacketCapturer):
    def __init__(self, process_orchestrator: ProcessOrchestrator):
        super().__init__(process_orchestrator)
