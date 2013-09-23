import sys
sys.path.append("../AVCommon")

import logging, sys
import logging.config

import test_logging_child


formatter = logging.Formatter('%(asctime)s -%(levelname)s- %(filename)s:%(lineno)s   %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
logger=logging.getLogger('')
logger.addHandler(stdout_handler)
logger.setLevel(logging.DEBUG)
logging.debug('A debug message')
logging.info('Some information')
logging.warning('A shot across the bows')

logging.config.fileConfig('../logging.conf')
logging.debug('A debug message')
logging.info('Some information')

logging.warning('A shot across the bows')

test_logging_child.ClassName("calling a child")
