from hashlib import md5
from dpkt.tcp import TCP
from numba import njit
from numpy import in1d, all as numpy_all, array as numpy_array

# tutte le regole consentito di default
# il pacchetto viene bloccato se una delle regole viene attivata
# P <list of int> -> osserva una porta in src
# (in caso di risposta del server o dst in caso di richiesta dal client)
# B <bytes>,[[-]<offset>] -> controlla se son presenti dei bytes nel pacchetto
# b <bytes> -> controlla se son presenti de bytes nel payload
# R <regex> -> controlla se una stringa regex matcha nel payload
# L <int>/<min int>-<max int> -> controlla la lunghezza del pacchetto in modo fisso o dinamico
# ! -> affiancarlo alle lettere P, B, b, R, L fa il modo di negare
# esempi
# L 15 -> blocca i pacchetti di 15 bytes
# L 15\nP 8080 -> blocca i pacchetti di 15 byte che arrivano sulla 8080
# !P 9090 -> blocca tutti i pacchetti eccetto quelli sulla 9090
# b 0x20 -> blocca tutti i pacchetti che presentano uno spazio nel payload
# T <tag>

# True -> trigger della regola
# False -> non triggera la regola

#TODO implement FW_BANNED_PORTS

class Rule:
    @staticmethod
    def compute_md5(rule_str):
        return md5(rule_str.encode('utf-8')).hexdigest()

    def __init__(self, rule_str):
        self.rule_str = rule_str
        self.rule_id = Rule.compute_md5(rule_str)
        self._default_ports_behavior = False # non triggerano
        self.target_ports = None
        self.checkers = {}
        self.parse_rule(rule_str)

    def parse_rule(self, rule_str):
        for line in rule_str.split('\n'):
            index = 1 if line[index] == '!' else 0
            if line[index] == 'P':
                self._default_ports_behavior = bool(index)
                self.target_ports = {int(port):not index for port in line[index+2:].split(',')}
            elif line[index] == 'B':
                pass
            elif line[index] == 'b':
                pass
            elif line[index] == 'R':
                self.checkers
            elif line[index] == 'L':
                if '-' in line:
                    min_int, max_int = line[index+2:].split('-')
                    self.checkers['L'] = lambda numpy_packet:self.check_for_len(numpy_packet, int(min_int), int(max_int), mask=index)
                else:
                    num = int(line[index+2:].split(','))
                    self.checkers['L'] = lambda numpy_packet:self.check_for_len(numpy_packet, num, num+1, mask=index)

    def check_for_bytes_inside_package(self, numpy_packet, _bytes, mask=0):
        pass

    @njit(parallel=True)
    def check_for_bytes_inside_payload(self, numpy_packet, _bytes, mask=0):
        bytes_len = len(_bytes)
        for numpy_index in range(0, numpy_packet.shape[-1], bytes_len):
            for byte_index in range(bytes_len):
                if _bytes[byte_index] != numpy_packet[numpy_index+bytes_len]:
                    break
            else:
                return True
        return False

    def check_for_regex(self, numpy_packet, regex, mask=0):
        pass

    def check_for_len(self, numpy_packet, min_len, max_len, mask=0):
        return (max_len > numpy_packet.shape[-1] >= min_len) ^ (not mask)

    def judge(self, packet, numpy_packet, tags=set()):
        tcp_pkt = TCP(packet)
        return self.target_ports.get(tcp_pkt.sport(), self._default_ports_behavior)\
            and all(check(numpy_packet) for check in self.checkers.values())

    def get_hash(self):
        return self.rule_id
    
    def __hash__(self):
        return self.rule_id
