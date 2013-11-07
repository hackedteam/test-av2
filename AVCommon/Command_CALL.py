import logging

import command
from procedure import Procedure
from protocol import Protocol


#noinspection PyPep8Naming
class Command_CALL(command.MetaCommand):
    """ calls another procedure """
    def execute(self, args):
        logging.debug("    CS Execute")
        protocol, proc_name = args

        proc = Procedure.procedures[proc_name]
        protocol.procedure.insert(proc)

        return True, ""
