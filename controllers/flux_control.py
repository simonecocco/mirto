import fnfqueue
from controllers.firewall.firewall_logic import FuocoDiMuro
from controllers.fingerprinter import Fingerprinter
from numpy import array as numpy_array, ubyte
import logging
from utils.const import *
import numpy as np

main_process_lock = None
main_logger = None
main_shared_dict = None

def init_queue_conn(queue_num):
    queue_conn = fnfqueue.Connection()

    try:
        queue_conn.bind(queue_num)
        main_logger.info(f"Queue {queue_num} bound")
        queue_conn.queue[queue_num].set_mode(0xFFFF, fnfqueue.COPY_PACKET)
    except PermissionError:
        main_logger.error("Permission denied. Please run as root.")
        exit(1)

    return queue_conn

def queues_handler(queue_conn, firewall, fingerprinter):
    main_logger.info("Queue handler started")
    
    # Pre-alloca un buffer per i pacchetti
    packet_buffer = bytearray(65536)  # Max MTU size
    
    for packet in queue_conn:
        # Utilizza memoryview per evitare copie
        packet_view = memoryview(packet.payload)
        numpy_arr_val = np.frombuffer(packet_view, dtype=ubyte)
        
        with main_process_lock:
            # Usa append diretto con numpy array
            main_shared_dict[PACKET_ARRAY_KEY].append(numpy_arr_val.copy())
        
        # Esegui fingerprinting e firewalling
        cluster_id = fingerprinter.predict(numpy_arr_val)
        res = firewall.judge(packet, numpy_arr_val)
        
        if main_logger.isEnabledFor(logging.INFO):
            main_logger.info(f"Packet processed: {res} cluster: {cluster_id}")

def start_queue(process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict

    firewall = FuocoDiMuro(process_lock, logger, shared_dict)
    fingerprinter = Fingerprinter(main_logger, main_process_lock, main_shared_dict)

    queue_num = main_shared_dict[QUEUE_NUM_KEY]
    queue_conn = init_queue_conn(queue_num)

    queues_handler(queue_conn, firewall, fingerprinter)