from flask import Flask, request, jsonify
from subprocess import run as run_cmd
from utils.const import *
from controllers.firewall.rule import Rule

app = Flask(__name__)

main_process_lock = None
main_logger = None
main_shared_dict = None

@app.route('/hw', methods=['GET'])
def check_hello_world():
    return "Hello, World!", 200

@app.route('/packets', methods=['GET'])
def get_samples():
    start_offset = request.args.get('from', 0)
    with main_process_lock:
        arr_len = len(main_shared_dict['packet_array'])
        max_len = request.args.get('to', arr_len)
        assert start_offset + max_len <= arr_len and start_offset >= 0
        packets = [
            {'n':index+start_offset, 'bytes':pkt_bytes.tolist()}
            for index, pkt_bytes in enumerate(main_shared_dict['packet_array'][start_offset:start_offset+max_len])
        ]

    return jsonify({'packets': packets}), 200

@app.route('/packets', methods=['DELETE'])
def delete_pkts():
    start_offset = request.args.get('from', 0)
    with main_process_lock:
        arr_len = len(main_shared_dict['packet_array'])
        max_len = request.args.get('to', arr_len)
        assert start_offset + max_len <= arr_len and start_offset >= 0
        del main_shared_dict['packet_array'][start_offset:start_offset+max_len]

    return f'deleted {max_len - start_offset} packets', 200

def iptables_rules_mng(action, port):
    for direction in ['OUTPUT', 'INPUT']:
        for comm_port in ['s', 'd']:
            for proto in ['tcp', 'udp']:
                run_cmd([
                    'sudo', 'iptables',
                    action, direction,
                    '-p', proto,
                    f'--{comm_port}port', str(port),
                    '-j', 'NFQUEUE', '--queue-num', str(main_shared_dict.get(QUEUE_NUM_KEY, DEFAULT_QUEUE_NUM))
                ])

@app.route('/services/<port>', methods=['POST'])
def add_service(port):
    port = int(port)
    alias = request.args.get('alias', f'service_{port}')
    main_logger.info(f'creating rule for {port} ({alias})')
    iptables_rules_mng('-A', port)

    with main_process_lock:
        main_shared_dict[SERVICES_KEY][port] = alias

    return f'services at {port} ({alias}) added correctly', 200

@app.route('/services', methods=['GET'])
def get_services():
    packets_copy = None
    with main_process_lock:
        packets_copy = dict(main_shared_dict[SERVICES_KEY])
    return jsonify(packets_copy), 200

@app.route('/services/<port>', methods=['DELETE'])
def delete_service(port):        
    iptables_rules_mng('-D', port)

    with main_process_lock:
        try:
            del main_shared_dict[SERVICES_KEY][port]
        except:
            pass

    return f'{port} unregistered with success', 200

@app.route('/rule/<rule_str>', methods=['POST'])
def create_rule(rule_str):
    if rule_str not in main_shared_dict[FW_RULES_LIST]:
        main_shared_dict[FW_RULES_LIST].append(rule_str)
        return 'OK', 200
    return 'RULE ALREADY ADDED', 400

@app.route('/rule', methods=['GET'])
def get_rules():
    responses = []
    for rule_str in main_shared_dict[FW_RULES_LIST]:
        responses.append({'id':Rule.compute_md5(rule_str), 'str':rule_str})
    return jsonify(responses), 200

@app.route('/rule/<rule_hash>', methods=['DELETE'])
def delete_rule():
    if rule_hash in main_shared_dict[FW_RULES_HASH_SET].keys():
        del main_shared_dict[FW_RULES_HASH_SET][rule_hash]
        return 'OK', 200
    return 'HASH NOT VALID', 400


def start_rest_api(flask_port, process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict
    app.run(host='0.0.0.0', port=flask_port)
