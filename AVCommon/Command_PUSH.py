import os
import sys
import logging

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

import command
from AVMaster import vm_manager

#TODO
class Command_PUSH(command.ServerCommand):
    """ Pulls a set of files from a vm """
    def execute(self, args):
        """ server side """
        logging.debug("    CS PUSH")
        assert self.vm, "null self.vm"
        assert len(args) == 3 and isinstance(args, list), "PUSH expects a list of 3 elements"

        src_files,src_dir,dst_dir = args
        assert isinstance(src_files, list), "PUSH expects a list of src files"

        #TODO: push files to self.vm
#        files = {}

#        src,dst = args
#        vm_manager.execute(self.vm, "copyFileToGuest", src, dst)
#        print files
#        print "########"
#        print src_files,src_dir,dst_dir
#        print "########"
        memo = []
        for src_file in src_files:
            print src_file

            try:
                d, f = src_file.split("/")
            except ValueError:
                d = ""
                f = src_file

            src = "%s/%s/%s" % (src_dir, d, f)

            if d == "":
                dst = "%s\\%s" % (dst_dir, f)
            else:
                dst = "%s\\%s\\%s" % (dst_dir, d, f)

            rdir = "%s\\%s" % (dst_dir, d)
            if not rdir in memo:
                logging.debug("mkdir %s " % (rdir))
                vm_manager.execute(self.vm, "mkdirInGuest", rdir)
                memo.append(rdir)

            logging.debug("%s copy %s -> %s" % (self.vm, src, dst))
            vm_manager.execute(self.vm, "copyFileToGuest", src, dst)

        return True, "Files copied on VM"
