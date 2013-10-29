import logging

import command


class Command_BEGIN(command.ServerCommand):
    """ server side """
    def execute(self, args):
        logging.debug("    CS Execute")
        return True, "I'm doing Science and I'm alive"
