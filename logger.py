import logging
logging.basicConfig(filename='logging/log.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

# 
logging.debug('This is a debugging message')
logging.info('This is a info message')
logging.warning('This is a warning message')
logging.error('This is an error message')