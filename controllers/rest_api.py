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

@app.route('/service', methods=['POST'])
def add_service():
    port = int(request.json['port'])
    alias = request.json.get('alias', f'service_{port}')
    for direction in ['OUTPUT', 'INPUT']:
        for comm_port in ['s', 'd']:
            for proto in ['tcp', 'udp']:
                run_cmd([
                    'sudo', 'iptables',
                    '-A', direction,
                    '-p', proto,
                    f'--{comm_port}port', str(port),
                    '-j', 'NFQUEUE', '--queue-num', str(IN_QUEUE)
                ])
    with main_process_lock:
        main_shared_dict['services'] = main_shared_dict['services'][port] = alias

    return f'services at {port} ({alias}) added correctly'

@app.route('/service', methods=['GET'])
def get_services():
    with main_process_lock:
        services = {
            service_port:main_shared_dict['services'][service_port]
            for service_port in main_shared_dict['services'].keys()
        }

    return jsonify(services)

@app.route('/service', methods=['DELETE'])
def delete_service():
    pass

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
