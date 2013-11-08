import logging

import command


#noinspection PyPep8Naming
class Command_BEGIN(command.ServerCommand):
    """ begins a command, not really useful """
    def execute(self, args):
        logging.debug("    CS Execute")
        command.context = {}
        return True, "I'm doing Science and I'm alive"
