from controllers.firewall.rule import Rule
from utils.const import *
from numba import njit

'''
PACKET
.drop()
.accept(mangle:int=0) -> MANGLE_MARK o MANGLE_PAYLOAD
.mangle()
.verdict(action:int, mangle:int=0) -> DROP, ACCEPT, REPEAT, STOP
Raises NoSuchAttributeException
.cap_len -> payload_len
.gid -> packet uid
.hw_protocol -> HW protocol id
.hook -> netfilter hook id
.time -> packet arrival time
.truncated ->true if packet payload is truncated
.uid -> packet uid
.mark -> get and set, unsigned integer 32bit
.payload -> set value needs to be byte
'''

class FuocoDiMuro:
    def __init__(self, process_lock, logger, shared_dict, rules=[]):
        assert rules is not None, 'rule can\'t be none!'

        self.main_process_lock = process_lock
        self.main_logger = logger
        self.main_shared_dict = shared_dict

        self.rules = {}
        self.fw_str_rules_copy = {rule_str for rule_str in self.main_shared_dict[FW_RULES_LIST]}
        for rule in self.main_shared_dict[FW_RULES_LIST]:
            rule_obj = Rule(rule)
            self.rules[rule_obj.get_hash()] = rule_obj
            self.main_logger.info(f'new rule {rule}')

    def get_rules(self):
        return self.rules.values()

    def delete_rule(self, rule_or_id):
        if type(rule_or_id) is str and rule_or_id in self.rules:
            del self.rules[rule_or_id]
        elif type(rule_or_id) is Rule and rule_or_id.get_hash() in self.rules:
            del self.rules[rule_or_id.get_hash()]

    def __sub__(self, rule_or_id):
        self.delete_rule(rule_or_id)

    def get_rule(self, rule_id):
        return self.rules.get(rule_id, None)

    def __getitem__(self, rule_id):
        return self.get_rule(rule_id)

    def add_rule(self, rule_str):
        rule_obj = Rule(rule_str)
        self.rules[rule_obj.get_hash()] = rule_obj
        return rule_obj

    def __add__(self, rule_str):
        return self.add_rule(rule_str)

    def check_for_new_rule(self):
        actual_rules = set(self.main_shared_dict[FW_RULES_LIST])
        actual_rules_len = len(actual_rules)
        rules_len = len(self.rules)
        if actual_rules_len == rules_len: # nessuna modifica
            return
        elif actual_rules_len > rules_len: # aggiunte
            for added_rule in actual_rules-{rule.rule_str for rule in self.rules.values()}:
                r = Rule(added_rule)
                self.rules[r.get_hash()] = r
                self.main_logger.info(f'new rule {added_rule}')
        else: # actual_rules_len < rules_len: # eliminate
            for deleted_rule in {rule.rule_str for rule in self.rules.values()}-actual_rules:
                hash_md5 = Rule.compute_md5(deleted_rule)
                del self.rules[hash_md5]
                self.main_logger.info(f'deleted rule {deleted_rule}')

    def judge(self, packet, numpy_packet, tags=None):
        self.check_for_new_rule()
        result = all(rule.judge(packet, numpy_packet, tags) for rule in self.rules.values())
        if result:
            packet.accept()
        else:
            packet.drop()
        return result

    def __call__(self, packet):
        return self.judge(packet)