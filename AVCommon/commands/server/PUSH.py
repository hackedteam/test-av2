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

    src_files, src_dir, dst_dir = args
    if not src_dir:
        src_dir = ""
    assert isinstance(src_files, list), "PUSH expects a list of src files"

    all_src = []
    relative_parents = set()

    """ look if i need all files in one directory """
    for src_file in src_files:
        g = glob.glob(os.path.join(src_dir,src_file))
        print g
        for f in g:
            # s is the relative file, expanded by glob
            s = f.replace("%s/" % src_dir,"")
            all_src.append(s)

            # add all the parents to the relative_parents set, to avoid repetitions
            p = os.path.split(s)[0]
            while p and p != src_dir:
                relative_parents.add(p)
                p = os.path.split(p)[0]

    # sorts the parents by length, so that parent is always before its sons
    parents = list(relative_parents)
    parents.sort(lambda x,y: len(x) - len(y))
    logging.debug("parents: %s" % parents)

    ntdir = lambda x: x.replace("/","\\")

    for r in parents:
        rdir = ntdir(os.path.join(dst_dir, r))
        logging.debug("mkdir %s " % (rdir))
        vm_manager.execute(vm, "mkdirInGuest", rdir)

    """ then upload parsed files """
    logging.debug("All files to copy are:\n%s" % src_files)
    for src_file in all_src:

        src = os.path.join(src_dir, src_file)
        dst = ntdir(os.path.join(dst_dir, src_file))

        logging.debug("%s copy %s -> %s" % (vm, src, dst))
        r = vm_manager.execute(vm, "copyFileToGuest", src, dst)

        if r > 0:
            return False, "Cant Copy %s on VM" % src_file

    return True, "Files copied on VM"

