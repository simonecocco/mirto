import logging
from time import time
from os import mkdir
from os.path import exists, join
from random import randint


LOG_FILES_DIRECTORY = './logs'


def get_logs_dir():
    return LOG_FILES_DIRECTORY


def get_log_filename():
    return f'log-{randint(0, 69104):0>5}-{time()}.log'


def get_log_path():
    if not exists(get_logs_dir()):
        mkdir(get_logs_dir())
        
    return join(get_logs_dir(), get_log_filename())


def get_logging_formatter():
    formatter = logging.Formatter(
        '(Mirto)[{asctime}][{levelname}] -> {message}',
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )
    return formatter


def get_logging_streamhandler():
    handler = logging.StreamHandler()
    handler.setFormatter(get_logging_formatter())
    return handler


def get_logging_filehandler(filename):
    handler = logging.FileHandler(filename, mode='w', encoding='utf-8')
    handler.setFormatter(get_logging_formatter())
    return handler


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(get_logging_streamhandler())
    log_file_path = get_log_path()
    logger.addHandler(get_logging_filehandler(log_file_path))
    logger.setLevel(logging.DEBUG)

    return logger
