import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager


#noinspection PyPep8Naming
class Command_PULL(command.ServerCommand):
    """ Pulls a set of files from a vm """

    def execute(self, args):
        """ server side """
        logging.debug("    CS Execute")
        assert self.vm, "null self.vm"
        assert len(args) == 3 and isinstance(args, list), "PULL expects a list of 3 elements"

        #TODO pull files from self.vm
        src_files, src_dir, dst_dir = args
        assert isinstance(src_files, list), "PULL expects a list of src files"

        memo = []
        for src_file in src_files:
            print src_file
            try:
                d, f = src_file.split("\\")
            except ValueError:
                d = ""
                f = src_file

            src = "%s\\%s\\%s" % (src_dir, d, f)

            if d == "":
                dst = "%s/%s" % (dst_dir, f)
            else:
                dst = "%s/%s/%s" % (dst_dir, d, f)

            rdir = "%s/%s" % (dst_dir, d)
            if not rdir in memo:
                if not os.path.exists(rdir):
                    logging.debug("mkdir %s " % (rdir))
                    os.mkdir(rdir)
                    memo.append(rdir)

            logging.debug("%s copy %s -> %s" % (self.vm, src, dst))
            vm_manager.execute(self.vm, "copyFileFromGuest", src, dst)

        return True, "Files copied from VM"
