from hashlib import md5
from dpkt.tcp import TCP
import numpy as np
import re
from typing import Dict, Set, Callable, List
from functools import lru_cache

class Rule:
    _BYTES_PATTERN = re.compile(r'0x([0-9a-fA-F]+)')
    _RANGE_PATTERN = re.compile(r'(\d+)-(\d+)')
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def compute_md5(rule_str: str) -> str:
        return md5(rule_str.encode('utf-8')).hexdigest()

    def __init__(self, rule_str: str) -> None:
        self.rule_str: str = rule_str.strip()
        self.rule_id: str = self.compute_md5(self.rule_str)
        self._default_ports_behavior: bool = True
        self.target_ports: Dict[int, bool] = {}
        self.checkers: List[Callable[[np.ndarray], bool]] = []
        self._compiled_bytes: Dict[str, np.ndarray] = {}
        self._compiled_regex = None
        self.parse_rule()

    def parse_rule(self):
        for line in self.rule_str.split('\n'):
            if not line:
                continue
                
            negated = line.startswith('!')
            content = line[1:] if negated else line
            rule_type = content[0]
            rule_value = content[2:].strip()
            
            if rule_type == 'P':
                self._default_ports_behavior = not negated
                self.target_ports.update(
                    (int(port), not negated) 
                    for port in rule_value.split(',')
                    if port.strip()
                )
            elif rule_type == 'B':
                # Bytes in packet
                pattern = self._compile_bytes(rule_value)
                checker = lambda p, pat=pattern, neg=negated: self._check_bytes(p, pat, neg)
                self.checkers.append(checker)
            elif rule_type == 'b':
                # Bytes in payload
                pattern = self._compile_bytes(rule_value)
                checker = lambda p, pat=pattern, neg=negated: self._check_payload(p, pat, neg)
                self.checkers.append(checker)
            elif rule_type == 'R':
                # Regex
                self._compiled_regex = re.compile(rule_value.encode())
                checker = lambda p, reg=self._compiled_regex, neg=negated: self._check_regex(p, reg, neg)
                self.checkers.append(checker)
            elif rule_type == 'L':
                # Length check
                if '-' in rule_value:
                    match = self._RANGE_PATTERN.match(rule_value)
                    if match:
                        min_len, max_len = map(int, match.groups())
                        checker = lambda p, mn=min_len, mx=max_len, neg=negated: self._check_length(p, mn, mx, neg)
                else:
                    length = int(rule_value.split(',')[0])
                    checker = lambda p, l=length, neg=negated: self._check_length(p, l, l+1, neg)
                self.checkers.append(checker)

    @staticmethod
    def _compile_bytes(byte_str: str) -> np.ndarray:
        if byte_str.startswith('0x'):
            hex_str = byte_str[2:]
            return np.array(
                [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)],
                dtype=np.uint8
            )
        return np.frombuffer(byte_str.encode(), dtype=np.uint8)

    def _check_bytes(self, packet: np.ndarray, pattern: np.ndarray, negated: bool) -> bool:
        # Usa correlazione per trovare il pattern
        if len(pattern) > len(packet):
            return negated
        
        # Operazione vettoriale ottimizzata
        for i in range(len(packet) - len(pattern) + 1):
            if np.array_equal(packet[i:i+len(pattern)], pattern):
                return not negated
        return negated

    def _check_payload(self, packet: np.ndarray, pattern: np.ndarray, negated: bool) -> bool:
        # Simile a _check_bytes ma potrebbe saltare l'header
        return self._check_bytes(packet[20:], pattern, negated)  # Assume header IP+TCP di 20 byte

    def _check_regex(self, packet: np.ndarray, pattern: re.Pattern, negated: bool) -> bool:
        match = pattern.search(packet.tobytes())
        return (match is not None) ^ negated

    @staticmethod
    def _check_length(packet: np.ndarray, min_len: int, max_len: int, negated: bool) -> bool:
        length = len(packet)
        return (min_len <= length < max_len) ^ negated

    def judge(self, packet, numpy_packet, tags=None) -> bool:
        try:
            tcp_pkt = TCP(packet.payload)
            port_check = (
                self.target_ports.get(tcp_pkt.sport, self._default_ports_behavior) or
                self.target_ports.get(tcp_pkt.dport, self._default_ports_behavior)
            )
            
            if not port_check:
                return False
                
            return all(checker(numpy_packet) for checker in self.checkers)
        except Exception:
            return False

    def get_hash(self) -> str:
        return self.rule_id
    
    def __hash__(self) -> int:
        return hash(self.rule_id)
