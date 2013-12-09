__author__ = 'fabrizio'

import logging
import logging.config
import yaml

with open("../logging.yml") as o:
    logging.config.dictConfig(yaml.load(o))