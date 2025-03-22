from flask import Flask, request, jsonify
from subprocess import run as run_cmd
from controllers.flux_control import IN_QUEUE

app = Flask(__name__)

main_process_lock = None
main_logger = None
main_shared_dict = None

@app.route('/hw', methods=['GET'])
def check_hello_world():
    return "Hello, World!"

@app.route('/packets', methods=['GET'])
def get_samples():
    with main_process_lock:
        packets = list(main_shared_dict['packet_array'])

    return jsonify({'packets': packets})

def iptables_rules_mng(action, port):
    for direction in ['OUTPUT', 'INPUT']:
        for comm_port in ['s', 'd']:
            for proto in ['tcp', 'udp']:
                run_cmd([
                    'sudo', 'iptables',
                    action, direction,
                    '-p', proto,
                    f'--{comm_port}port', str(port),
                    '-j', 'NFQUEUE', '--queue-num', str(IN_QUEUE)
                ])

@app.route('/services/<port>', methods=['POST'])
def add_service(port):
    port = int(port)
    alias = request.args.get('alias', f'service_{port}')
    main_logger.info(f'creating rule for {port} ({alias})')
    iptables_rules_mng('-A', port)

    with main_process_lock:
        main_shared_dict['services'][port] = alias

    return f'services at {port} ({alias}) added correctly'

@app.route('/services', methods=['GET'])
def get_services():
    with main_process_lock:
        return jsonify(dict(main_shared_dict['services']))

@app.route('/services/<port>', methods=['DELETE'])
def delete_service(port):        
    iptables_rules_mng('-D', port)

    with main_process_lock:
        try:
            del main_shared_dict['services'][port]
        except:
            pass

    return f'{port} unregistered with success'

@app.route('/rule', methods=['POST'])
def create_rule():
    pass

@app.route('/rule', methods=['GET'])
def get_rules():
    pass

@app.route('/rule', methods=['DELETE'])
def delete_rule():
    pass

def start_rest_api(flask_port, process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict
    app.run(host='0.0.0.0', port=flask_port)
