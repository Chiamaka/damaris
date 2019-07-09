import os
import logging


def logger():
    LOG_FORMAT = "%(levelname)s %(asctime)s %(message)s"
    log_file = os.path.join(os.getcwd(), 'log_file.log')
    logging.basicConfig(filename=log_file,
                        level=logging.INFO, format=LOG_FORMAT)
    log = logging.getLogger(__name__)
    return log
