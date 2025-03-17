from flask import Flask, request, jsonify

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

def start_rest_api(flask_port, process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict
    app.run(host='0.0.0.0', port=flask_port)
