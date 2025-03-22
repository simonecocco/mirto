from hashlib import md5

class Rule:
    __slots__ = [
        'rule_id',
        'attributes',
        'action',
        'rule_str'
    ]
    def __init__(self, rule_str='+'):
        self.rule_str = rule_str
        self.rule_id = md5(rule_str.encode('utf-8')).hexdigest()
        self.action, tmp_attributes = rule_str.split(',')
        self.attributes = {}

        for attribute in tmp_attributes:
            tmp = attribute.split(':', maxsplit=1)
            self.attributes[tmp[0]] = self.attributes.get(tmp[0], []) + [tmp[1]]

    def judge(self, packet, tags):
        pass

    def get_hash(self):
        return self.rule_id
    
    def __hash__(self):
        return self.rule_id
