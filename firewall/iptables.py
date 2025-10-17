from typing import List
from utils.command_executer import CommandExecutor
from firewall.iptables_rule import IptablesRule


class IptablesRuleManager:
    _sudo_prefix = ['sudo', 'iptables']

    def __init__(self, executor=CommandExecutor()):
        self._executor = executor
        self._added_rules = set()

    def _concat_rule_flag_prefix(self, flag, rule: List[str]) -> List[str]:
        prefix = IptablesRuleManager._sudo_prefix
        prefix.append(flag)
        return prefix + rule

    def _concat_append_prefix(self, rule: List[str]) -> List[str]:
        return self._concat_rule_flag_prefix('-A', rule)

    def _concat_insert_prefix(self, rule: List[str]) -> List[str]:
        return self._concat_rule_flag_prefix('-I', rule)

    def _concat_remove_prefix(self, rule: List[str]) -> List[str]:
        return self._concat_rule_flag_prefix('-D', rule)

    def add_rule(self, rule: IptablesRule):
        raw_rule = rule.get_rule()
        if raw_rule in self._added_rules:
            return

        self._added_rules.add(raw_rule)
        complete_rule = self._concat_append_prefix(raw_rule)
        self._executor.execute(complete_rule)

    def remove_rule(self, rule: IptablesRule):
        raw_rule = rule.get_rule()
        if raw_rule not in self._added_rules:
            return

        self._added_rules.remove(raw_rule)
        complete_rule = self._concat_remove_prefix(raw_rule)
        self._executor.execute(complete_rule)
