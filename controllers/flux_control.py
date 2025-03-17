import fnfqueue
import dpkt
from controllers.firewall.firewall_logic import init_fw, judge

main_process_lock = None
main_logger = None
main_shared_dict = None

IN_QUEUE = 1
OUT_QUEUE = 2

def init_queue_conn():
    queue_conn = fnfqueue.Connection()

    try:
        queue_conn.bind(IN_QUEUE)
        queue_conn.bind(OUT_QUEUE)
        queue_conn.queue[IN_QUEUE].set_mode(0xFFFF, fnfqueue.COPY_PACKET)
        queue_conn.queue[OUT_QUEUE].set_mode(0xFFFF, fnfqueue.COPY_PACKET)
    except PermissionError:
        main_logger.error("Permission denied. Please run as root.")
        exit(1)

    return queue_conn

def queues_handler(queue_conn):
    main_logger.info("Queue handler started")

    for packet in queue_conn:
        try:
            ip = dpkt.ip.IP(packet.payload)
        except dpkt.UnpackError:
            continue

        main_logger.debug(ip)
        judge(packet, ip)


def start_queue(process_lock, logger, shared_dict):
    global main_process_lock
    global main_logger
    global main_shared_dict

    main_process_lock = process_lock
    main_logger = logger
    main_shared_dict = shared_dict

    init_fw(process_lock, logger, shared_dict)

    queue_conn = init_queue_conn()
    queues_handler(queue_conn)