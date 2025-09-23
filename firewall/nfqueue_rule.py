from typing import List
from firewall.iptables_rule import IptablesRule


class NfqueueRule(IptablesRule):
    _FLAG_SOURCE_PORT = '--sport'
    _FLAG_DEST_PORT = '--dport'

    def __init__(self, direction, source_dest, port, queue_num=1):
        assert port > 0
        assert direction in set(['INPUT', 'OUTPUT'])
        assert source_dest in set([
            NfqueueRule._FLAG_SOURCE_PORT,
            NfqueueRule._FLAG_DEST_PORT
        ])

        self._rule = [
            direction,
            '-p', IptablesRule.PROTOCOL_TCP,
            source_dest, str(port),
            '-j', 'NFQUEUE', '--queue-num', queue_num
        ]

    def get_rule(self) -> List[str]:
        return self._rule

