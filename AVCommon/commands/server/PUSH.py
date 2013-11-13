import os
import sys
import glob
import logging

from AVMaster import vm_manager

def execute(vm, args):
    """ server side """
    logging.debug("    CS PUSH")
    assert vm, "null self.vm"
    assert len(args) == 3 and isinstance(args, list), "PUSH expects a list of 3 elements"

    src_files,src_dir,dst_dir = args
    assert isinstance(src_files, list), "PUSH expects a list of src files"

    memo = []
    all_src = []

    """ look if i need all files in one directory """
    for src_file in src_files:
        if "*" in src_file:
            print "####\nFound * in %s\n####" % src_file
            print glob.glob(os.path.join(src_dir,src_file))
            for f in glob.glob(os.path.join(src_dir,src_file)):
                all_src.append(f.replace("/%s" % src_dir,""))
        else:
            all_src.append(src_file)

    """ then upload parsed files """
    logging.debug("All files to copy are:\n%s" % src_files)
    for src_file in all_src:
        print "#####\n%d\n###" % len(src_file.split("/"))
        try:
            d, f = src_file.split("/")
        except ValueError:
            d = ""
            f = src_file

        src = "%s/%s/%s" % (src_dir, d, f)

        if d == "":
            print "#####\nd:%s\nf:%s\n###" % (dst_dir,f)
            dst = "%s\\%s" % (dst_dir, f)
        else:
            print "#####\nd:%s\nf:%s\n###" % (d,f)
            dst = "%s\\%s\\%s" % (dst_dir, d, f)

        rdir = "%s\\%s" % (dst_dir, d)

        if not rdir in memo:
            logging.debug("mkdir %s " % (rdir))
            vm_manager.execute(vm, "mkdirInGuest", rdir)
            memo.append(rdir)

        logging.debug("%s copy %s -> %s" % (vm, src, dst))
        r = vm_manager.execute(vm, "copyFileToGuest", src, dst.replace("/","\\"))

        if r > 0:
            return False, "Cant Copy %s on VM" % src_file

    return True, "Files copied on VM"

