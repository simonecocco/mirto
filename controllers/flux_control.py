import fnfqueue
from controllers.firewall.firewall_logic import FuocoDiMuro
from controllers.fingerprinter import Fingerprinter
from numpy import array as numpy_array, ubyte
from utils.const import *

main_process_lock = None
main_logger = None
main_shared_dict = None

def init_queue_conn(queue_num):
    queue_conn = fnfqueue.Connection()

    try:
        queue_conn.bind(queue_num)
        queue_conn.queue[queue_num].set_mode(0xFFFF, fnfqueue.COPY_PACKET)
    except PermissionError:
        main_logger.error("Permission denied. Please run as root.")
        exit(1)

    return queue_conn

def queues_handler(queue_conn, firewall):
    main_logger.info("Queue handler started")
    #fingerprinter = Fingerprinter()

    for packet in queue_conn:
        with main_process_lock:
            main_shared_dict[PACKET_ARRAY_KEY].append(numpy_array([b for b in packet.payload], dtype=ubyte))
        
        #cluster_id = 
        judge(packet)

    #TODO logger
            


def start_queue(process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict

    init_fw(process_lock, logger, shared_dict)
    firewall = FuocoDiMuro(process_lock, logger. shared_dict)

    queue_num = get_queue_num(main_shared_dict)
    queue_conn = init_queue_conn()

    queues_handler(queue_conn)