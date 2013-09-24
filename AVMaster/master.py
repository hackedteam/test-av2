import os
import sys
import argparse

prev = os.path.join(os.getcwd(), "..")
if not prev in sys.path:
    sys.path.append(prev)

from AVCommon import Procedure


class Master():
    """docstring for Master"""
    def __init__(self, args):
        self.args = args

    def start():
        vm_names = self.args.vm.split(",")

        vms = [ AVMachine(vm) for vm in vm_names]

        procedures = Procedure.loadFromFile("procedures.yaml")
        proc = procedures[vm.procedure]

        assert proc, "cannot find the specified procedure: %s" % vm.procedure
        dispatcher = Dispatcher(vms, procedures)

        dispatcher.startServer()


def main():
    parser = argparse.ArgumentParser(description='AVMonitor master.')
    args = parser.parse_args()
    parser.add_argument('-m', '--vm', required=False,
                        help="Virtual Machine where execute the operation")
    parser.add_argument('-v', '--verbose', action='verbose_true', default=False,
                        help="Verbose")
    parser.add_argument('-p', '--procedure', type=str, default=False,
                        help="Procedure to execute")

    master = Master(args)
    master.start()

if __name__ == '__main__':
    main()
