# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(logger_name=""):
    # logging setting
    LOGGER = logging.getLogger(logger_name)
    LOGGER.setLevel(logging.INFO)

    LOG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'logdir')
    print("LOG_DIR=%s\n" % LOG_DIR)
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    handler = RotatingFileHandler(filename=os.path.join(LOG_DIR, 'LOGGER.log'), maxBytes=104857600, backupCount=2)  # 104857600 Byte = 100 MB
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('>>>>> %(asctime)s %(levelname)-5s >>> %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    return LOGGER


LOG = get_logger("es2es")
