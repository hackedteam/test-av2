import os
import sys
import argparse

sys.path.append(os.path.split(os.getcwd())[0])
sys.path.append(os.getcwd())

from AVCommon import procedure


class Master():
    """docstring for Master"""

    def __init__(self, args):
        self.args = args

    def start():
        vms = [AVMachine(vm) for vm in vm_names]

        procedures = procedure.load_from_file("procedures.yaml")
        proc = procedures[vm.procedure]

        assert proc, "cannot find the specified procedure: %s" % vm.procedure
        dispatcher = Dispatcher(vms, procedures)

        dispatcher.start_server()

    def on_finished(self, vm):
        pass


def main():
    parser = argparse.ArgumentParser(description='AVMonitor master.')
    args = parser.parse_args()
    parser.add_argument('-m', '--vm', required=False,
                        help="Virtual Machine where execute the operation")
    parser.add_argument('-v', '--verbose', action='verbose_true', default=False,
                        help="Verbose")
    parser.add_argument('-r', '--procedure', type=str, default=False,
                        help="Procedure to execute")
    parser.add_argument('-p', '--pool', type=int, required=False,
                        help="This is the number of parallel process (default 8)")

    master = Master(args)
    master.start()


if __name__ == '__main__':
    main()
