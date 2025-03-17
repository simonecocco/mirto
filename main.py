from argparse import ArgumentParser
import logging
from multiprocessing import Process, Lock, Manager
from controllers.flux_control import start_queue
from controllers.rest_api import start_rest_api

def main(args, logger):
    logger.info("Mirto started")

    multiprocessing_manager = Manager()
    shared_dict = multiprocessing_manager.dict()
    packet_array = multiprocessing_manager.list()
    shared_dict['packet_array'] = packet_array
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

    args = argparser.parse_args()

    logger = setup_logger()

    main(args, logger)