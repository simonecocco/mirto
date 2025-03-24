main_process_lock = None
main_logger = None
main_shared_dict = None

FIREWALL_RULES = []

def init_fw(process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict

    # TODO logica per le regole del firewall
    # TODO probabilmente controllando sha del file delle regole
    # TODO se cambia le ricarica

def judge(packet):
    '''
    PACKET
    .drop()
    .accept(mangle:int=0) -> MANGLE_MARK o MANGLE_PAYLOAD
    .mangle()
    .verdict(action:int, mangle:int=0) -> DROP, ACCEPT, REPEAT, STOP
    Raises NoSuchAttributeException
    .cap_len -> payload_len
    .gid -> packet uid
    .hw_protocol -> HW protocol id
    .hook -> netfilter hook id
    .time -> packet arrival time
    .truncated ->true if packet payload is truncated
    .uid -> packet uid
    .mark -> get and set, unsigned integer 32bit
    .payload -> set value needs to be byte
    '''
    # TODO
    packet.accept()