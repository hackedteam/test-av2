import logging

import command


#noinspection PyPep8Naming
class Command_UPDATE(command.ServerCommand):
    """ updates a vm """

    def execute(self, args):
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"

        #TODO: updates a self.vm, possibly just a sleep
        return True, ""


