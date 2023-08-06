import logging as lg
import os
from datetime import datetime

"""
    After init_logger() is called, logs will be written to 'logs/\{start time\}'.
    Logs can be written by importing logging and writing messages to 4 different levels:
        1. debug
        2. info
        3. warning
        4. error
    Logs will also be output to stdout.
"""


def init_logger():
    # create folder for logs
    logs_folder_path = "./logs/"
    try:
        os.mkdir(logs_folder_path)
    except OSError:
        print("Did not create new log directory %s", logs_folder_path)
    else:
        print("Successfully created log directory")

    # log parameters
    current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    current_log_path = logs_folder_path + current_time + ".log"
    lg.basicConfig(
        filename=current_log_path,
        format="%(asctime)s - %(levelname)s: %(message)s",
        level=lg.DEBUG,
    )
    lg.getLogger().addHandler(lg.StreamHandler())

    # sample log
    lg.info("Initialized logger")


# logging.debug('This is a debugging message')
# logging.info('This is a info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
