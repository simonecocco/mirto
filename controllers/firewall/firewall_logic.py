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

def judge(packet, ip_packet):
    # TODO
    packet.accept()