from json import dumps
from os import urandom
from flask import Flask, request, Response, Blueprint
from flask_basicauth import BasicAuth
from utils.const import *
from utils.generic import add_iptables_rule
from controllers.firewall.rule import Rule
from mirto.user.user_preferences import (
    DEFAULT_MIRTO_PORT_KEY,
    DEFAULT_MIRTO_HOST_KEY,
    DEFAULT_MIRTO_PASSWORD_KEY,
    DEFAULT_MIRTO_USERNAME_KEY,
)



def check_cred_completeness(prefix, cred):
    if cred is not None:
        return cred

    new_cred = prefix+''.join([
        hex(b)[2:]
        for b in urandom(12)
    ])
    print(f'used generated credential {new_cred}')



main_process_lock = None
main_logger = None
main_shared_dict = None

INTERNAL_ERROR = 'errore interno. notifica sysadmin'

def craft_response(message:str='', data=None, code=200):
    """Crea una risposta JSON standardizzata.

    Args:
        message (str, optional): Messaggio da includere nella risposta.  Defaults to ''.
        data (any, optional): Dati da includere nella risposta. Defaults to None.
        code (int, optional): Codice di stato HTTP per la risposta. Defaults to 200.

    Returns:
        Response: Un oggetto Response di Flask contenente i dati JSON, 
                   il messaggio e il codice di stato specificati.

    Raises:
        TypeError: se 'code' non è un intero.
    """

    if not isinstance(code, int):
        raise TypeError("Il codice di stato 'code' deve essere un intero.")

    return Response(dumps({
        'message': message,
        'data': data,
    }), status=code, mimetype='application/json')

@app.route('/packets', methods=['GET'])
#@auth.required
def get_samples():
    try:
        start_offset = request.args.get('from', 0)
        with main_process_lock:
            arr_len = len(main_shared_dict[PACKET_ARRAY_KEY])
            max_len = request.args.get('to', arr_len)
            assert start_offset + max_len <= arr_len and start_offset >= 0, LookupError(f'Indici fuori dal range massimo (0-{arr_len})')
            assert arr_len != 0, BufferError('Array vuota!')
            packets = [
                {'n':index+start_offset, 'bytes':pkt_bytes.tolist()}
                for index, pkt_bytes in enumerate(main_shared_dict['packet_array'][start_offset:start_offset+max_len])
            ]
        return craft_response(message=f'retrieved {len(packets)} pkts', data=dumps({'packets': packets}), code=200)
    except LookupError as le:
        main_logger.error(le)
        return craft_response(message=str(le), data=dumps({'packets': []}), code=400)
    except BufferError as be:
        main_logger.error(be)
        return craft_response(message=str(be), data=dumps({'packets': []}), code=200)
    except Exception as generic_exception:
        main_logger.error(generic_exception)
        return craft_response(message=INTERNAL_ERROR, data=dumps({'packets': []}), code=500)


# TODO TBA
#@app.route('/packets', methods=['DELETE'])
#def delete_pkts():
#    start_offset = request.args.get('from', 0)
#    with main_process_lock:
#        arr_len = len(main_shared_dict['packet_array'])
#        max_len = request.args.get('to', arr_len)
#        assert start_offset + max_len <= arr_len and start_offset >= 0
#        del main_shared_dict['packet_array'][start_offset:start_offset+max_len]
#
#    return f'deleted {max_len - start_offset} packets', 200

def iptables_rules_mng(action, port):
    queue_num = str(main_shared_dict.get(QUEUE_NUM_KEY, DEFAULT_QUEUE_NUM))
    for direction in ['OUTPUT', 'INPUT']:
        for comm_port in ['s', 'd']:
            for proto in ['tcp', 'udp']:
                add_iptables_rule(action, direction, proto, comm_port, port, queue_num)

@app.route('/services/<port>', methods=['POST'])
#@auth.required
def add_service(port):
    try:
        port = int(port)
        alias = request.args.get('alias', f'service_{port}')
        main_logger.info(f'creating rule for {port} ({alias})')
        iptables_rules_mng('-A', port)

        with main_process_lock:
            main_shared_dict[SERVICES_KEY][port] = alias

        return craft_response(message=f'services at {port} ({alias}) added correctly', code=200)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/services', methods=['GET'])
#@auth.required
def get_services():
    try:
        with main_process_lock:
            services_copy = dict(main_shared_dict[SERVICES_KEY])
        return craft_response(data=dumps(services_copy), code=200)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/services/<port>', methods=['DELETE'])
#@auth.required
def delete_service(port):
    try:
        iptables_rules_mng('-D', port)

        with main_process_lock:
            try:
                del main_shared_dict[SERVICES_KEY][port]
            except:
                pass

        return craft_response(message=f'{port} unregistered with success', code=200)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/rule/<rule_str>', methods=['POST'])
#@auth.required
def create_rule(rule_str):
    try:
        rule_hash = Rule.compute_md5(rule_str)
        if rule_hash not in main_shared_dict[FW_RULES_HASH_SET]:
            main_shared_dict[FW_RULES_HASH_SET][rule_hash] = rule_str
            return craft_response(message=f'rule "{rule_str}" created', code=200)
        return craft_response(message='rule already added', code=400)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/rule', methods=['GET'])
#@auth.required
def get_rules():
    try:
        resp = [
            {'id': rule_hash, 'str': rule_str}
            for rule_hash, rule_str in main_shared_dict[FW_RULES_HASH_SET].items()
        ]
        return craft_response(data=dumps(resp), code=200)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/rule/<rule_hash>', methods=['DELETE'])
#@auth.required
def delete_rule(rule_hash):
    try:
        if rule_hash in main_shared_dict[FW_RULES_HASH_SET].keys():
            del main_shared_dict[FW_RULES_HASH_SET][rule_hash]
            return craft_response(message=f'{rule_hash} deleted', code=200)
        return craft_response(message='hash non valido', code=200)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)


class MirtoAPI:
    APP_USERNAME_KEY = 'BASIC_AUTH_USERNAME'
    APP_PASSWORD_KEY = 'BASIC_AUTH_PASSWORD'

    def __init__(self, process_orchestrator):
        self._process_orchestrator = process_orchestrator
        self._app = self._configure_app()
        self._auth = BasicAuth(self._app)
        self._register_blueprints()

    def _configure_app(self):
        app = Flask(__name__)
        app.logger = self._process_orchestrator.get_logger()

        user_pref = self._process_orchestrator.get_user_prefs()
        mirto_username = user_pref.mirto_config.get(DEFAULT_MIRTO_USERNAME_KEY)
        mirto_password = user_pref.mirto_config.get(DEFAULT_MIRTO_PASSWORD_KEY)

        self._app.config[MirtoAPI.APP_USERNAME_KEY] = mirto_username
        self._app.config[MirtoAPI.APP_PASSWORD_KEY] = mirto_password

        return app

    def _register_blueprints(self):
        self._app._register_blueprints #TODO

    def run(self):
        user_pref = self._process_orchestrator.get_user_prefs()

        api_host = user_pref.mirto_config[DEFAULT_MIRTO_HOST_KEY]
        api_port = user_pref.mirto_config[DEFAULT_MIRTO_PORT_KEY]

        self._app.run(host=api_host, port=api_port)

    @self._app.route('/status')
    def get_status(self):
        return Response('OK', status=200)
    

def start_rest_api(process_orchestrator):
    api_interface = MirtoAPI(process_orchestrator)
