from typing import Union
from utils.process_orchestrator import ProcessOrchestrator
from utils.system_checker import SystemChecker
from capturer.nfqueue_capturer import NFQueueCapturer
from capturer.dpkt_capturer import DPKTCapturer
from capturer.file_capturer import FileCapturer


class PacketListenerFactory:
    def __init__(self, process_orchestrator: ProcessOrchestrator):
        self._process_orchestrator: ProcessOrchestrator = process_orchestrator

    def get_capturer(self, input_file: Union[str, None] = None):
        if input_file:
            return FileCapturer(self.orchestrator, input_file)

        if SystemChecker.is_nfnetlink_queue_available():
            return NFQueueCapturer(self.orchestrator)
        else:
            return DPKTCapturer(self.orchestrator)
