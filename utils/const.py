DEFAULT_QUEUE_NUM = 1
QUEUE_NUM_KEY = 'queue-num'
PACKET_ARRAY_KEY = 'packet_array'
SERVICES_KEY = 'services'
FW_NOT_APPLICABLE_PORTS = [22]
FW_RULES_LIST = 'firewall-rules'
FW_RULES_HASH_SET = 'fw-rules-hashes'

def get_queue_num(shared_dict):
    return shared_dict.get(QUEUE_NUM_KEY, DEFAULT_QUEUE_NUM)