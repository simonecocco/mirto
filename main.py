from argparse import ArgumentParser
import logging
from multiprocessing import Process, Lock, Manager
from controllers.flux_control import start_queue
from controllers.rest_api import start_rest_api
from utils.const import *

def main(args, logger):
    logger.info("Mirto started")

    multiprocessing_manager = Manager()
    shared_dict = multiprocessing_manager.dict()
    shared_dict[PACKET_ARRAY_KEY] = multiprocessing_manager.list()
    shared_dict[SERVICES_KEY] = multiprocessing_manager.dict()
    shared_dict[QUEUE_NUM_KEY] = args.queue_num
    shared_dict[FW_RULES_LIST] = multiprocessing_manager.list() #deprecated
    shared_dict[FW_RULES_HASH_SET] = multiprocessing_manager.dict()

    process_lock = Lock()
    processes = [
        Process(target=start_queue, args=(process_lock, logger, shared_dict)),
        Process(target=start_rest_api, args=(args.port, process_lock, logger, shared_dict))
    ]

    try:
        for process in processes: process.start()
        for process in processes: process.join()
    except KeyboardInterrupt:
        for process in processes: process.terminate()
        for process in processes: process.join()

    logger.info("Mirto stopped")

def setup_logger():
    logger = logging.getLogger("Mirto")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-p', '--port', type=int, default=6969)
    argparser.add_argument('-F', '--pcap-file', type=str, default=None, help='File to use to pre-train')
    argparser.add_argument('-N', '--queue-num', type=int, default=DEFAULT_QUEUE_NUM)

    args = argparser.parse_args()

    logger = setup_logger()

    main(args, logger)