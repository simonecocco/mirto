from typing import Dict, Set
from threading import Lock
from collections import defaultdict
from controllers.firewall.rule import *
import logging
from utils.const import *

class FuocoDiMuro:
    def __init__(self, process_lock, logger, shared_dict, rules=None):
        self.main_process_lock = process_lock
        self.main_logger = logger
        self.main_shared_dict = shared_dict
        
        # Strutture dati ottimizzate
        self.rules: Dict[str, Rule] = {}
        self._rule_hashes: Set[str] = set()
        self._update_lock = Lock()
        
        if rules:
            for rule in rules:
                self.add_rule(rule)

    def get_rules(self):
        return list(self.rules.values())

    def delete_rule(self, rule_or_id):
        with self._update_lock:
            if isinstance(rule_or_id, str):
                self.rules.pop(rule_or_id, None)
            elif isinstance(rule_or_id, Rule):
                self.rules.pop(rule_or_id.get_hash(), None)

    def __sub__(self, rule_or_id):
        self.delete_rule(rule_or_id)
        return self

    def get_rule(self, rule_id):
        return self.rules.get(rule_id)

    def __getitem__(self, rule_id):
        return self.get_rule(rule_id)

    def add_rule(self, rule_str):
        with self._update_lock:
            rule = Rule(rule_str)
            self.rules[rule.get_hash()] = rule
            return rule

    def __add__(self, rule_str):
        return self.add_rule(rule_str)

    def _update_rules(self):
        with self._update_lock:
            current_hashes = set(self.main_shared_dict[FW_RULES_HASH_SET].keys())
            
            # Aggiunte
            added = current_hashes - self._rule_hashes
            for rule_hash in added:
                rule_str = self.main_shared_dict[FW_RULES_HASH_SET][rule_hash]
                self.rules[rule_hash] = Rule(rule_str)
                if self.main_logger.isEnabledFor(logging.INFO):
                    self.main_logger.info(f'New rule added: {rule_str[:50]}...')
            
            # Rimozioni
            removed = self._rule_hashes - current_hashes
            for rule_hash in removed:
                self.rules.pop(rule_hash, None)
                if self.main_logger.isEnabledFor(logging.INFO):
                    self.main_logger.info(f'Rule deleted: {rule_hash}')
            
            self._rule_hashes = current_hashes

    def judge(self, packet, numpy_packet, tags=None):
        self._update_rules()
        
        try:
            # Verifica tutte le regole in parallelo (se possibile)
            result = all(rule.judge(packet, numpy_packet, tags) 
                        for rule in self.rules.values())
            
            if result:
                packet.accept()
            else:
                packet.drop()
                
            return result
        except Exception as e:
            self.main_logger.error(f"Error judging packet: {e}")
            packet.accept()  # Fail-open per sicurezza
            return True

    def __call__(self, packet, numpy_packet):
        return self.judge(packet, numpy_packet)
