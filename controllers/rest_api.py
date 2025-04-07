from json import dumps
from os import urandom
from flask_basicauth import BasicAuth
from flask import Flask, Response, request, jsonify, render_template
from subprocess import run as run_cmd
from utils.const import *
from utils.generic import add_iptables_rule
from controllers.firewall.rule import Rule
from user.config import WEBAPP_USERNAME, WEBAPP_PASSWORD

app = Flask(__name__)

def check_cred_completeness(prefix, cred):
    if cred is not None:
        return cred

    new_cred = prefix+''.join([
        hex(b)[2:]
        for b in urandom(12)
    ])
    print(f'used generated credential {new_cred}')

app.config['BASIC_AUTH_USERNAME'] = check_cred_completeness('username_', WEBAPP_USERNAME)
app.config['BASIC_AUTH_PASSWORD'] = check_cred_completeness('psw_', WEBAPP_PASSWORD)

auth = BasicAuth(app)

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

@app.route("/home")
def home():
    return render_template("index.html")

@app.route('/hw', methods=['GET'])
#@auth.required
def check_hello_world():
    """
    Endpoint che restituisce un messaggio "Hello World".

    Questo endpoint risponde a richieste GET all'URL '/hw'.
    Restituisce un oggetto response creato dalla funzione `craft_response`
    con il messaggio impostato a "Hello World".

    Returns:
        A Flask response object containing the message "Hello World".
    """
    return craft_response(message='Hello World')

@app.route('/packets', methods=['GET'])
#@auth.required
def get_samples():
    """
    Restituisce un sottoinsieme dei pacchetti memorizzati in memoria condivisa.

    Questo endpoint consente di recuperare una porzione di pacchetti memorizzati
    in `main_shared_dict['packet_array']`, specificando un intervallo tramite
    i parametri 'from' e 'to'.

    Args:
        None

    Returns:
        flask.Response: Una risposta JSON contenente i pacchetti richiesti.
                        La risposta include:
                            - 'message': Un messaggio di stato.
                            - 'data': Una stringa JSON contenente una lista di pacchetti
                                       nel formato `{'packets': [...]}`.  Ogni pacchetto
                                       è rappresentato come `{'n': index, 'bytes': [bytes]}`.
                            - 'code': Il codice di stato HTTP (200, 400 o 500).

    Raises:
        LookupError: Se gli indici 'from' e 'to' specificati sono fuori dall'intervallo valido.
        BufferError: Se l'array di pacchetti in memoria condivisa è vuoto.
        Exception: In caso di altri errori imprevisti, viene registrato un errore nel logger
                   e viene restituito un codice di stato 500.

    Query Parameters:
        from (int, optional): L'indice di inizio dell'intervallo da recuperare. Default: 0.
        to (int, optional): L'indice di fine dell'intervallo da recuperare (escluso).
                           Se non specificato, viene utilizzato l'indice di fine dell'array.
    """
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
    """Gestisce le regole di iptables per il traffico di rete.

    Questa funzione crea o elimina regole di iptables per il traffico in entrata e in uscita,
    sia TCP che UDP, per una determinata porta e coda (queue).

    Args:
        action (str): L'azione da eseguire. '-A' per aggiungere una regola, '-D' per eliminarla.
        port (int): La porta su cui applicare la regola.

    Returns:
        None

    Raises:
        ValueError: Se 'action' non è né '-A' né '-D'.
        TypeError: Se 'port' non è un intero.

    Note:
        La funzione utilizza `main_shared_dict` per ottenere il numero di coda (queue number).
        Se la chiave `QUEUE_NUM_KEY` non è presente in `main_shared_dict`, viene utilizzato il
        valore predefinito `DEFAULT_QUEUE_NUM`.
        Utilizza la funzione `add_iptables_rule` per aggiungere o eliminare le regole specifiche.
    """
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

@app.route('/label/<label_num>', methods=['GET'])
#@auth.required
def get_label(label_num):
    try:
        label_num = int(label_num)
        label = main_shared_dict[FINGERPRINTER_LABELS_KEY].get(label_num, None)
        return craft_response(
            message='this label doesn\'t exists' if label is None else '',
            data=dumps({'label_num':label_num, 'label_str':label}),
            code=200
        )
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/labels', methods=['GET'])
#@auth.required
def get_labels():
    try:
        return craft_response(
            data=dumps([
                {'label_num':label_num, 'label_str':label}
                for label_num, label in main_shared_dict[FINGERPRINTER_LABELS_KEY].items()
            ])
        )
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

@app.route('/label/<label_num>/<new_label>', methods=['POST'])
#@auth.required
def set_label(label_num, new_label):
    try:
        label_num = int(label_num)
        if label_num in main_shared_dict[FINGERPRINTER_LABELS_KEY]:
            prev_label = main_shared_dict[FINGERPRINTER_LABELS_KEY][label_num]
            main_shared_dict[label_num] = new_label
            return craft_response(message='label changed correctly', data={'from':prev_label, 'to':new_label}, code=200)
        else:
            return craft_response(message='invalid label', code=400)
    except Exception as e:
        main_logger.error(e)
        return craft_response(message=INTERNAL_ERROR, code=500)

def start_rest_api(flask_port, process_lock, logger, shared_dict):
    """Avvia l'API REST Flask.

    Questa funzione configura le variabili globali per il lock del processo,
    il logger e il dizionario condiviso, e quindi avvia l'applicazione Flask.

    Args:
        flask_port (int): La porta su cui ascoltare per le richieste API.
        process_lock (threading.Lock): Un lock per la sincronizzazione tra processi.
        logger (logging.Logger): L'oggetto logger per il logging di eventi.
        shared_dict (dict): Un dizionario condiviso tra i processi.
    """
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict
    app.run(host='0.0.0.0', port=flask_port)
