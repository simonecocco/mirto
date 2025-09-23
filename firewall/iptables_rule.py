from abc import ABC, abstractmethod
from typing import List


class IptablesRule(ABC):
    PROTOCOL_TCP = 'tcp'

    @abstractmethod
    def get_rule(self) -> List[str]:
        pass
