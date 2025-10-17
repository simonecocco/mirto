from capturer.base_capturer import BasePacketCapturer
from utils.process_orchestrator import ProcessOrchestrator


class FileCapturer(BasePacketCapturer):
    def __init__(self, process_orchestrator: ProcessOrchestrator, input_file):
        super().__init__(process_orchestrator)
        self._file_path: str = input_file
